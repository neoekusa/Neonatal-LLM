# Crossed logistic sensitivity analysis. Arguments: long-format CSV, output directory.
suppressPackageStartupMessages(library(lme4))
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Usage: Rscript crossed_random_effects.R LONG_CSV OUTPUT_DIR")
d <- read.csv(args[1], stringsAsFactors = FALSE)
required <- c("Failure", "Number", "Model", "Complexity", "Cognitive", "Task")
if (!all(required %in% names(d)) || anyNA(d[required])) stop("Incomplete analysis data")
if (!all(d$Failure %in% c(0, 1)) || anyDuplicated(d[c("Number", "Model")])) {
  stop("Expected one binary outcome per question and model")
}
if (!all(table(d$Number, d$Model) == 1L)) stop("Incomplete question-by-model panel")

d$Number <- factor(d$Number)
d$Model <- factor(d$Model)
d$Complexity <- relevel(factor(d$Complexity), "Low")
d$Cognitive <- relevel(factor(d$Cognitive), "Remember")
d$Task <- relevel(factor(d$Task), "1_Physiology_and_Pathophysiology")

ctrl <- glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 200000),
                     check.rankX = "stop.deficient")
full <- glmer(Failure ~ Cognitive + Complexity + Task + (1 | Number) + (1 | Model),
              data = d, family = binomial(), control = ctrl)
reduced <- update(full, . ~ . - Complexity)
for (fit in list(full, reduced)) {
  if (!isTRUE(fit@optinfo$conv$opt == 0) || length(fit@optinfo$conv$lme4$messages) ||
      isSingular(fit) || any(!is.finite(vcov(fit)[]))) {
    stop("Crossed fit did not provide a nonsingular converged estimate")
  }
}
effects <- coef(summary(full))
terms <- c("ComplexityModerate", "ComplexityHigh")
limits <- confint(full, parm = terms, method = "Wald")
lrt <- anova(reduced, full)
vc <- as.data.frame(VarCorr(full))
out <- data.frame(
  level = c("Moderate", "High"), reference = "Low",
  conditional_odds_ratio = exp(effects[terms, "Estimate"]),
  ci_low = exp(limits[terms, 1]), ci_high = exp(limits[terms, 2]),
  p_value = effects[terms, "Pr(>|z|)"], lrt_chi2 = lrt$Chisq[2],
  lrt_df = lrt$Df[2], lrt_p = lrt[["Pr(>Chisq)"]][2],
  sd_question = vc$sdcor[vc$grp == "Number"], sd_model = vc$sdcor[vc$grp == "Model"],
  questions = nlevels(d$Number), models = nlevels(d$Model), responses = nrow(d),
  r_version = as.character(getRversion()), lme4_version = as.character(packageVersion("lme4"))
)
dir.create(args[2], showWarnings = FALSE, recursive = TRUE)
write.csv(out, file.path(args[2], "crossed_random_effects.csv"), row.names = FALSE)
