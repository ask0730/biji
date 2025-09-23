# 1.https连接不稳定，使用ssh连接：

创建ssh秘钥:
git Bash:

检查是否已有 SSH 密钥
ls -la ~/.ssh

若无现有密钥，生成新的
ssh-keygen -t ed25519 -C "2137576215@qq.com"


回车两次，使用默认路径和空密码


启动 SSH 代理
eval "$(ssh-agent -s)"


 添加私钥到代理
ssh-add ~/.ssh/id_rsa


复制公钥内容
cat ~/.ssh/id_rsa.pub | clip






在 GitHub 添加 SSH 密钥:
登录 GitHub，点击右上角头像 → Settings
左侧菜单选择 SSH and GPG keys
点击 New SSH key
在 Title 栏输入标识
在 Key 栏粘贴复制的公钥内容
点击 Add SSH key


验证配置是否成功：
ssh -T git@github.com
yes

首次连接提示：
The authenticity of host 'github.com (20.205.243.166)' can't be established.
ED25519 key fingerprint is SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'github.com' (ED25519) to the list of known hosts.
Hi ask0730! You've successfully authenticated, but GitHub does not provide shell access.


输入：yes
Hi ask0730! You've successfully authenticated, but GitHub does not provide shell access.



使用SSH 协议操作仓库：
先进入项目目录
# 克隆仓库（如果还没克隆）
git clone git@github.com:ask0730/biji.git

# 或者如果已经有本地仓库，更换远程地址
git remote set-url origin git@github.com:ask0730/biji.git

# 然后执行拉取操作
git pull --tags origin main


推送代码
git push origin main