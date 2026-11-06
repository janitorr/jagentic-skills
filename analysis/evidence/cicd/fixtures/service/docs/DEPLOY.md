# Deployment target

- Azure subscription: `00000000-0000-0000-0000-000000000000`
- Resource group: `rg-orders`
- Container registry: `ordersacr.azurecr.io`
- Staging App Service: `orders-api-staging`
- Production App Service: `orders-api-prod`
- Both App Services run the container image from the registry.
- Staging deploys automatically from `main`.
- Production requires an approval.
- GitHub uses federated credentials (OIDC); Azure DevOps uses the
  `orders-azure` service connection.
- The pipeline is used from both GitHub and Azure Repos, so produce both
  variants for the same commit.
