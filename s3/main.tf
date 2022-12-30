//noinspection MissingModule
module "this" {
  source                  = "terraform-aws-modules/s3-bucket/aws"
  version                 = "3.6.0"
  bucket_prefix           = "terraform-backend-"
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  versioning = {
    status     = true
    mfa_delete = false
  }

  server_side_encryption_configuration = {
    rule = {
      apply_server_side_encryption_by_default = {
        sse_algorithm = "AES256"
      }
    }
  }
}
