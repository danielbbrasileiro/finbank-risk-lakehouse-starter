# AWS Free-Tier Blueprint

This Terraform module documents the minimum AWS surface for the FinBank Risk Lakehouse cloud path.

It is intentionally small and cost-aware:

- one private S3 bucket for bronze/silver/gold objects;
- bucket versioning for auditability;
- server-side encryption;
- public access blocked;
- lifecycle cleanup for short-lived demo objects.

Run only when you intentionally want to provision cloud resources:

```bash
cd infra/aws
terraform init
terraform fmt
terraform validate
terraform plan -var="bucket_name=<globally-unique-demo-bucket>"
```

`terraform apply` is optional and not required for the local portfolio demo.
