1、首次push， 被拒绝，403：https://www.cnblogs.com/kn-zheng/p/17025185.html
. vim .git/config （编辑这个项目仓库目录下的config文件）。
. 找到[remote "origin"]域。
. 把url = https://xxx@github.com...   修改为   url = ssh://git@github.com...
. 保存并退出。 