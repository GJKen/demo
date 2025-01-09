import os
import requests

# 获取 Personal Access Token (PAT)
token = os.getenv('GITHUB_PAT')

# GitHub API 信息
owner = 'your-username'  # 请替换为您的 GitHub 用户名
repo = 'your-repository'  # 请替换为您的仓库名
api_url = f'https://api.github.com/repos/{owner}/{repo}/issues'

# 验证 token 是否有效
if not token:
    print("GITHUB_PAT is not set.")
    exit(1)

# 遍历 recover_issues 文件夹中的 .md 文件
md_folder = 'recover_issues'
for filename in os.listdir(md_folder):
    if filename.endswith('.md'):
        issue_number, title = filename.replace('.md', '').split('_', 1)
        issue_number = int(issue_number)

        # 读取文件内容作为 issue 内容
        with open(os.path.join(md_folder, filename), 'r') as file:
            content = file.read()

        # 使用 GitHub API 恢复 issue
        response = requests.post(
            f'{api_url}/{issue_number}/reopen',
            headers={
                'Authorization': f'Bearer {token}',  # 使用 PAT 进行认证
                'Accept': 'application/vnd.github.v3+json'
            },
            json={
                'title': title,  # 用文件名中的标题
                'body': content  # 用文件内容作为 issue 内容
            }
        )

        if response.status_code == 200:
            print(f'Issue #{issue_number} reopened successfully')
        else:
            print(f'Failed to reopen issue #{issue_number}: {response.status_code}, {response.text}')