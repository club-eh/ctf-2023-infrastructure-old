# DNS records for flagship (ctf-2023.clubeh.ca)
resource "cloudflare_record" "flagship" {
  zone_id = data.cloudflare_zone.base.id
  type    = "A"
  ttl     = 300 # 5 minutes
  name    = var.subdomain
  value   = var.ip_flagship
}
resource "cloudflare_record" "flagship_wildcard" {
  zone_id = data.cloudflare_zone.base.id
  type    = "A"
  ttl     = 300 # 5 minutes
  name    = "*.${var.subdomain}"
  value   = var.ip_flagship
}

# DNS records for challenge servers (cs#.ctf-2023.clubeh.ca)
resource "cloudflare_record" "challenges" {
  zone_id = data.cloudflare_zone.base.id
  type    = "A"
  ttl     = 300 # 5 minutes

  for_each = var.ip_challenges

  name  = "cs${each.key}.${var.subdomain}"
  value = each.value
}
