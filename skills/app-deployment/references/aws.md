# AWS

Confirm commands with `aws <service> help` on the installed CLI, and confirm a service is still offered to new accounts before choosing it. This file is a map, not a transcript.

## Fits

Organizations already on AWS, or projects needing its specific services, regions, or compliance posture. More moving parts than a platform host; define infrastructure as code (CDK, Terraform, SAM, or CloudFormation) rather than by hand.

## Pick the service by shape

| Shape | Service |
| --- | --- |
| Static site or SPA | S3 bucket behind CloudFront |
| Framework web app with Git-based deploys and PR previews | Amplify Hosting |
| Containerized API or worker | ECS on Fargate, behind a load balancer |
| Event-driven or low-traffic API | Lambda with API Gateway or a function URL |
| Single server you manage | EC2 or Lightsail; follow `vps.md` |

## Authentication

- Local: a named profile, ideally through IAM Identity Center (`aws sso login`).
- CI: OpenID Connect to assume an IAM role with the official credentials action. Do not store long-lived access keys in CI.
- Scope the deploy role to the resources it deploys.

## Configuration and secrets

Secrets Manager or SSM Parameter Store. Reference them from the task definition or function configuration by ARN so values never appear in templates or logs.

## Preview deploy

Only Amplify Hosting gives per-pull-request previews out of the box. Otherwise keep a staging environment (a separate stack, ideally a separate account) and deploy there first.

## Production deploy

- **S3 + CloudFront:** `aws s3 sync <build-dir> s3://<bucket> --delete`, then `aws cloudfront create-invalidation --distribution-id <id> --paths "/*"`. Keep the bucket private behind origin access control.
- **ECS:** build and push the image to ECR, register a new task definition revision, `aws ecs update-service --cluster <c> --service <s> --task-definition <family:rev>`, then `aws ecs wait services-stable`. Enable the deployment circuit breaker with rollback.
- **Lambda:** `aws lambda update-function-code`, publish a version, and move an alias to it; or `sam deploy`.

## Rollback

- S3 + CloudFront: re-sync the previous build artifact and invalidate. Keep build artifacts, or enable bucket versioning.
- ECS: update the service back to the previous task definition revision; the circuit breaker does this automatically on failed health checks.
- Lambda: point the alias at the previous version.
- Infrastructure: redeploy the previous template revision.

## Logs

CloudWatch Logs: `aws logs tail <log-group> --follow`.

## CI notes

Tag images with the commit SHA, never only `latest`, so a revision can be traced and rolled back.

## Gotchas

- Health-check path and grace period must match the app's startup time, or ECS will cycle healthy tasks.
- CloudFront caches aggressively; hash asset filenames and keep HTML short-lived.
- Resources left running cost money. List what was created and how to remove it.
