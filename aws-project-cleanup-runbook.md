# AWS Project Cleanup Runbook

## Project 2 AWS Resource Cleanup

A safe, repeatable procedure for identifying, deleting, and validating AWS resources created during an AWS Agentic AI project.

> **Important:** Never blindly delete AWS resources. Always identify, validate, delete, and verify resources in stages.

---

## 1. Purpose

AWS projects using Amazon Bedrock, AgentCore, Lambda, API Gateway, S3, DynamoDB, CloudWatch, IAM, and CloudFormation can create resources that continue to exist after project work ends.

This runbook removes project-specific resources while preserving required shared/bootstrap infrastructure.

---

## 2. Safety Principles

Before deleting any resource, verify:

- Resource name and ID
- AWS Region
- Creation date
- Project association
- Dependencies
- Whether it is shared
- Whether it is managed by CloudFormation/CDK

Do not delete an unused resource merely because it appears unused. It may be shared, required by another service, or part of CDK/bootstrap infrastructure.

### Never expose credentials

Never put AWS access keys, secret keys, session tokens, or credential files into GitHub, screenshots, documentation, or chat.

---

## 3. Before Starting

### Confirm Region

```bash
aws configure get region
```

For this project:

```text
us-east-1
```

If required:

```bash
export AWS_DEFAULT_REGION=us-east-1
```

### Confirm AWS Identity

```bash
aws sts get-caller-identity
```

Validate that the account and IAM role are the intended project/lab environment.

---

## 4. Recommended Cleanup Order

```text
1. Identify CloudFormation stacks
2. Inspect stack resources
3. Delete the project CloudFormation stack
4. Verify stack deletion
5. Identify standalone resources
6. Delete API Gateway
7. Delete Lambda functions
8. Clean Lambda IAM roles/policies
9. Delete project S3 bucket
10. Delete project CloudWatch log groups
11. Check DynamoDB
12. Identify/delete Bedrock Knowledge Base
13. Wait for Knowledge Base deletion
14. Clean Knowledge Base IAM role/policies
15. Check Bedrock Agents
16. Check AgentCore Runtime
17. Check AgentCore Memory
18. Perform final account/resource scan
19. Confirm only intentionally retained infrastructure remains
```

---

# 5. CloudFormation Cleanup

## Step 1: List stacks

```bash
aws cloudformation list-stacks   --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE   --query 'StackSummaries[].{Name:StackName,Status:StackStatus}'   --output table
```

Identify the application stack.

Do **not** automatically delete:

```text
CDKToolkit
```

## Step 2: Inspect stack resources

```bash
aws cloudformation list-stack-resources   --stack-name <PROJECT_STACK_NAME>   --query 'StackResourceSummaries[].{LogicalId:LogicalResourceId,Type:ResourceType,PhysicalId:PhysicalResourceId,Status:ResourceStatus}'   --output table
```

Review all resources before deletion.

## Step 3: Delete project stack

```bash
aws cloudformation delete-stack   --stack-name <PROJECT_STACK_NAME>
```

Check:

```bash
aws cloudformation describe-stacks   --stack-name <PROJECT_STACK_NAME>   --query 'Stacks[0].{Name:StackName,Status:StackStatus}'   --output table
```

Expected:

```text
DELETE_COMPLETE
```

or the stack disappears from the active stack list.

## Step 4: Validate

```bash
aws cloudformation list-stacks   --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE   --query 'StackSummaries[].{Name:StackName,Status:StackStatus}'   --output table
```

Only intentionally retained stacks should remain.

---

# 6. API Gateway Cleanup

## Step 1: List APIs

```bash
aws apigateway get-rest-apis   --query 'items[].{Name:name,Id:id,Created:createdDate}'   --output table
```

For a suspected API:

```bash
aws apigateway get-rest-api   --rest-api-id <API_ID>   --query '{Name:name,Id:id,Description:description,CreatedDate:createdDate}'   --output table
```

Check stages:

```bash
aws apigateway get-stages   --rest-api-id <API_ID>   --query 'item[].{Stage:stageName,Created:createdDate}'   --output table
```

## Step 2: Delete

```bash
aws apigateway delete-rest-api   --rest-api-id <API_ID>
```

## Step 3: Validate

```bash
aws apigateway get-rest-api   --rest-api-id <API_ID>
```

Expected after deletion:

```text
NotFoundException
```

---

# 7. Lambda Cleanup

## Step 1: List functions

```bash
aws lambda list-functions   --query 'Functions[].{Name:FunctionName,Runtime:Runtime,LastModified:LastModified}'   --output table
```

Confirm project ownership.

## Step 2: Delete

```bash
aws lambda delete-function   --function-name <FUNCTION_NAME>
```

## Step 3: Validate

```bash
aws lambda get-function   --function-name <FUNCTION_NAME>
```

Expected:

```text
ResourceNotFoundException
```

Then:

```bash
aws lambda list-functions   --query 'Functions[].FunctionName'   --output table
```

---

# 8. Lambda IAM Roles and Policies

## Step 1: Inspect role

```bash
aws iam get-role   --role-name <ROLE_NAME>
```

Inline policies:

```bash
aws iam list-role-policies   --role-name <ROLE_NAME>
```

Managed policies:

```bash
aws iam list-attached-role-policies   --role-name <ROLE_NAME>
```

## Step 2: Detach project-specific managed policy

```bash
aws iam detach-role-policy   --role-name <ROLE_NAME>   --policy-arn <POLICY_ARN>
```

## Step 3: Delete project-specific managed policy

```bash
aws iam delete-policy   --policy-arn <POLICY_ARN>
```

Do not delete shared/AWS-managed policies unless confirmed safe.

## Step 4: Delete role

After all policies are removed:

```bash
aws iam delete-role   --role-name <ROLE_NAME>
```

Validate:

```bash
aws iam get-role   --role-name <ROLE_NAME>
```

Expected:

```text
NoSuchEntity
```

---

# 9. S3 Cleanup

## Step 1: List buckets

```bash
aws s3 ls
```

Inspect a project bucket:

```bash
aws s3 ls s3://<BUCKET_NAME> --recursive
```

Confirm ownership before deletion.

## Step 2: Empty bucket

```bash
aws s3 rm s3://<BUCKET_NAME>   --recursive
```

## Step 3: Delete bucket

```bash
aws s3 rb s3://<BUCKET_NAME>
```

## Step 4: Validate

```bash
aws s3 ls
```

The project bucket should no longer appear.

### CDK bucket warning

A bucket such as:

```text
cdk-hnb659fds-assets-<ACCOUNT_ID>-<REGION>
```

is CDK bootstrap infrastructure.

**Do not delete it unless you intentionally want to remove the CDK bootstrap environment.**

---

# 10. CloudWatch Logs Cleanup

## Step 1: List log groups

```bash
aws logs describe-log-groups   --query 'logGroups[].{Name:logGroupName,StoredBytes:storedBytes}'   --output table
```

Identify project-specific groups.

## Step 2: Delete

```bash
aws logs delete-log-group   --log-group-name "<LOG_GROUP_NAME>"
```

## Step 3: Validate

```bash
aws logs describe-log-groups   --query 'logGroups[].logGroupName'   --output table
```

---

# 11. DynamoDB Cleanup

## Step 1: List tables

```bash
aws dynamodb list-tables   --output table
```

Inspect a suspected project table:

```bash
aws dynamodb describe-table   --table-name <TABLE_NAME>
```

## Step 2: Delete confirmed project table

```bash
aws dynamodb delete-table   --table-name <TABLE_NAME>
```

## Step 3: Validate

```bash
aws dynamodb list-tables   --output table
```

---

# 12. Amazon Bedrock Knowledge Base Cleanup

## Step 1: List Knowledge Bases

```bash
aws bedrock-agent list-knowledge-bases   --query 'knowledgeBaseSummaries[].{Name:name,Id:knowledgeBaseId,Status:status}'   --output table
```

Verify project ownership.

## Step 2: Inspect

If permissions allow:

```bash
aws bedrock-agent get-knowledge-base   --knowledge-base-id <KB_ID>   --output json
```

Check description, IAM role, storage configuration, and project association.

A lab role may return:

```text
AccessDeniedException
```

This means the current role lacks that permission. It does not by itself indicate a deletion failure.

## Step 3: Check data sources

```bash
aws bedrock-agent list-data-sources   --knowledge-base-id <KB_ID>   --query 'dataSourceSummaries[].{Name:name,Id:dataSourceId,Status:status}'   --output table
```

Do not delete a data source until ownership/dependencies are confirmed.

## Step 4: Delete Knowledge Base

```bash
aws bedrock-agent delete-knowledge-base   --knowledge-base-id <KB_ID>
```

Expected:

```json
{
    "knowledgeBaseId": "<KB_ID>",
    "status": "DELETING"
}
```

Deletion is asynchronous. Do not repeatedly issue delete commands.

## Step 5: Monitor

```bash
aws bedrock-agent list-knowledge-bases   --query 'knowledgeBaseSummaries[].{Name:name,Id:knowledgeBaseId,Status:status}'   --output table
```

`DELETING` is normal while AWS processes the request.

When complete, the Knowledge Base should disappear.

If:

```bash
aws bedrock-agent list-data-sources   --knowledge-base-id <KB_ID>
```

returns:

```text
ResourceNotFoundException
```

the Knowledge Base is no longer available.

---

# 13. Knowledge Base IAM Role Cleanup

Only perform this after the Knowledge Base has been confirmed deleted.

## Step 1: Inspect role

```bash
aws iam get-role   --role-name <KB_ROLE_NAME>
```

Check attached policies:

```bash
aws iam list-attached-role-policies   --role-name <KB_ROLE_NAME>
```

Check inline policies:

```bash
aws iam list-role-policies   --role-name <KB_ROLE_NAME>
```

Confirm the role is dedicated to the deleted Knowledge Base.

## Step 2: Detach policies

```bash
aws iam detach-role-policy   --role-name <KB_ROLE_NAME>   --policy-arn <POLICY_ARN>
```

## Step 3: Delete project-specific policies

```bash
aws iam delete-policy   --policy-arn <POLICY_ARN>
```

## Step 4: Delete role

```bash
aws iam delete-role   --role-name <KB_ROLE_NAME>
```

Validate:

```bash
aws iam get-role   --role-name <KB_ROLE_NAME>
```

Expected:

```text
NoSuchEntity
```

---

# 14. Bedrock Agents

List:

```bash
aws bedrock-agent list-agents   --query 'agentSummaries[].{Name:agentName,Id:agentId,Status:agentStatus}'   --output table
```

Do not automatically delete an agent. Verify project ownership first.

---

# 15. AgentCore Runtime

Use:

```bash
aws bedrock-agentcore-control list-agent-runtimes   --output table
```

Expected after cleanup:

```text
ListAgentRuntimes
```

with no project runtime rows.

---

# 16. AgentCore Memory

Use:

```bash
aws bedrock-agentcore-control list-memories   --output table
```

Expected:

```text
ListMemories
```

with no project memory rows.

---

# 17. Final Verification Commands

Run all of the following before declaring cleanup complete.

## CloudFormation

```bash
aws cloudformation list-stacks   --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE   --query 'StackSummaries[].{Name:StackName,Status:StackStatus}'   --output table
```

## S3

```bash
aws s3 ls
```

## Lambda

```bash
aws lambda list-functions   --query 'Functions[].FunctionName'   --output table
```

## API Gateway

```bash
aws apigateway get-rest-apis   --query 'items[].{Name:name,Id:id}'   --output table
```

## DynamoDB

```bash
aws dynamodb list-tables   --output table
```

## Bedrock Knowledge Bases

```bash
aws bedrock-agent list-knowledge-bases   --query 'knowledgeBaseSummaries[].{Name:name,Id:knowledgeBaseId,Status:status}'   --output table
```

## AgentCore Runtime

```bash
aws bedrock-agentcore-control list-agent-runtimes   --output table
```

## AgentCore Memory

```bash
aws bedrock-agentcore-control list-memories   --output table
```

## CloudWatch

```bash
aws logs describe-log-groups   --query 'logGroups[].{Name:logGroupName,StoredBytes:storedBytes}'   --output table
```

---

# 18. Final Cleanup Checklist

## AWS Identity

- [ ] Correct AWS account confirmed
- [ ] Correct AWS Region confirmed
- [ ] No credentials exposed in GitHub
- [ ] Temporary credentials not committed

## CloudFormation

- [ ] Project stack identified
- [ ] Stack resources inspected
- [ ] Project stack deleted
- [ ] Stack deletion validated
- [ ] CDKToolkit intentionally preserved

## AgentCore

- [ ] Project Runtime identified
- [ ] Project Runtime deleted
- [ ] Runtime count verified
- [ ] Project Memory identified
- [ ] Project Memory deleted
- [ ] Memory count verified

## Bedrock

- [ ] Project Knowledge Base identified
- [ ] Data sources checked where possible
- [ ] Knowledge Base deletion requested
- [ ] Knowledge Base deletion completed
- [ ] Project-specific KB IAM role identified
- [ ] IAM policies detached
- [ ] IAM policies deleted
- [ ] IAM role deleted
- [ ] Bedrock Agents checked

## Lambda

- [ ] Project Lambda functions identified
- [ ] Lambda functions deleted
- [ ] Lambda absence verified
- [ ] Lambda execution roles inspected
- [ ] Project-specific policies removed
- [ ] Project-specific roles removed

## API Gateway

- [ ] Project API identified
- [ ] API stages inspected
- [ ] API deleted
- [ ] API absence verified

## S3

- [ ] Project bucket identified
- [ ] Bucket contents inspected
- [ ] Bucket emptied
- [ ] Bucket deleted
- [ ] Bucket absence verified
- [ ] CDK asset bucket preserved

## CloudWatch

- [ ] Project log groups identified
- [ ] Project log groups deleted
- [ ] Log group list verified

## DynamoDB

- [ ] Tables inspected
- [ ] Project tables deleted if present
- [ ] Table list verified

---

# 19. Final Expected State

| Resource | Expected |
|---|---|
| Project CloudFormation stack | Deleted |
| Project AgentCore Runtime | Deleted |
| Project AgentCore Memory | Deleted |
| Project Bedrock Knowledge Base | Deleted |
| Project Bedrock IAM role | Deleted |
| Project Bedrock IAM policies | Deleted |
| Project Lambda functions | Deleted |
| Project Lambda IAM roles | Deleted |
| Project Lambda IAM policies | Deleted |
| Project API Gateway | Deleted |
| Project S3 bucket | Deleted |
| Project DynamoDB tables | Deleted |
| Project CloudWatch logs | Deleted |
| Project-specific Bedrock Agents | Deleted/None |
| Project-specific AgentCore resources | None |
| CDKToolkit | **KEEP** |
| CDK bootstrap asset bucket | **KEEP** |

---

# 20. Resources That Should Not Be Deleted Automatically

Do not delete these merely because they remain:

```text
CDKToolkit
```

```text
cdk-hnb659fds-assets-<ACCOUNT_ID>-<REGION>
```

Also do not automatically delete service roles such as:

```text
AmazonBedrockAgentCoreGatewayDefaultServiceRole...
AWSServiceRoleForBedrockAgentCoreRuntimeIdentity
```

unless separately verified as unused and safe to remove.

---

# 21. Common Errors

### ResourceNotFoundException

Usually means the resource has already been deleted.

### NoSuchEntity

Usually means the IAM entity has already been deleted.

### NotFoundException for API Gateway

After `delete-rest-api`, this confirms the API is gone.

### AccessDeniedException

Means the current IAM role lacks permission for that operation. It does not necessarily indicate a resource problem.

### DELETING

Means AWS accepted the deletion request but has not finished processing it. Do not repeatedly issue delete commands.

### DeleteConflict

For IAM roles, detach/delete project-specific policies before deleting the role.

---

# 22. Safe Cleanup Strategy

```text
DISCOVER
   ↓
IDENTIFY
   ↓
VERIFY OWNERSHIP
   ↓
INSPECT DEPENDENCIES
   ↓
DELETE
   ↓
WAIT
   ↓
VALIDATE
   ↓
FINAL SCAN
```

Never use a blanket "delete everything" approach.

---

# 23. Project 2 Cleanup Result

For this Project 2 environment, the following project-specific resources were removed:

- AgentCore Runtime
- AgentCore Memory
- CloudFormation application stack
- API Gateway
- Lambda functions
- Lambda IAM roles and policies
- S3 Knowledge Base bucket
- CloudWatch log groups
- Bedrock Knowledge Base
- Knowledge Base IAM execution role and policies

The final scan showed only intentionally retained CDK bootstrap infrastructure:

```text
CloudFormation:
CDKToolkit
```

and:

```text
S3:
cdk-hnb659fds-assets-<ACCOUNT_ID>-us-east-1
```

The project environment was therefore ready for the next AWS Agentic AI project.

---

# 24. Recommended Practice for Future Projects

At the beginning of every AWS project, maintain a resource inventory.

| Service | Resource | Created By | Project | Cleanup Required |
|---|---|---|---|---|
| CloudFormation | `<stack>` | CDK | Project | Yes |
| Lambda | `<function>` | CDK/manual | Project | Yes |
| API Gateway | `<api>` | CDK/manual | Project | Yes |
| S3 | `<bucket>` | CDK/manual | Project | Yes |
| Bedrock | `<knowledge-base>` | Manual/CDK | Project | Yes |
| AgentCore | `<runtime>` | CDK/manual | Project | Yes |
| AgentCore | `<memory>` | Manual/CDK | Project | Yes |
| IAM | `<role>` | CDK/manual | Project | Yes |
| CloudWatch | `<log-group>` | AWS service | Project | Yes |

This makes future cleanup easier and reduces the risk of leaving billable resources behind.

---

# 25. Final Rule

> **Always clean up project-specific resources and perform a final verification scan before moving to the next AWS project.**

Deleting local project code or shutting down a Codespace does not necessarily delete AWS resources.

Some resources may have been created outside CloudFormation and require separate cleanup.

**Always verify.**
