resource "aws_s3_bucket_lifecycle_configuration" "listing_media_archive" {
  bucket = aws_s3_bucket.listing_media.id

  rule {
    id     = "archive-sold-listing-photos"
    status = "Enabled"

    # Don't archive tiny objects: per-object transition + metadata overhead
    # outweighs the storage saving.
    filter {
      object_size_greater_than = 131072   # 128 KB
    }

    transition {
      # Was 30. Glacier bills a 90-day minimum, so archiving at day 30 makes
      # any deletion  in the next 90 days incur early-deletion fees.
      # Tune this number using real data on when deletion requests arrive.
      days          = 90
      storage_class = "GLACIER"
    }
  }

  rule {
    id     = "abort-incomplete-multipart"
    status = "Enabled"
    filter {}
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}