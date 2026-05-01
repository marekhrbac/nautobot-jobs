# Nautobot Job – AzurePipeline

This Nautobot Job validates VNet-related Prefix objects in Nautobot and triggers a GitLab CI/CD pipeline that provisions Azure infrastructure.

The job is intended to be used together with the `nautobot-azure` repository, where Terraform automation creates Azure Resource Groups and Virtual Networks based on data exported from Nautobot.

---
