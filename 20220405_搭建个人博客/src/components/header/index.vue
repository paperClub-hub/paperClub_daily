<template>
    <div>
        <div class="header-wrapper">
            <div class="header-main" >
                <div class="left-box">
                    <img src="../../assets/header-img.jpg" width="40 px" >
                    <span class="blog-title">我的个人博客</span>
                    <div class="article-cat-box">
                        <div class="cat-item">全部</div>
                        <div class="cat-item"> vue </div>
                        <div class="cat-item"> element-ui</div>
                    </div>
                </div>

                <el-menu mode="horizontal" v-if='authorName'>
                    <el-submenu index="login-set">
                        <template slot="title">
                            欢迎{{authorName}}
                        </template>
                    </el-submenu>
                </el-menu>

                <div v-if="!isLogin" class="right-box">
                    <div  @click="login('login')" class="login">登录</div>
                    <div  @click="login('register')" class="register">注册</div>
                </div>
            </div>
        </div>
        
        <div class="dialog"> 
            <el-dialog
                :title="loginType == 'login' ? '登录' : '注册'"
                width="30%"
                :close-on-click-modal="false"
                :visible.sync="dialogVisible"
                >
                <el-form 
                    :model="ruleForm" 
                    :rules="rules" 
                    ref="ruleForm" 
                    label-width="100px" 
                    class="demo-ruleForm">
                    <!--  输入用户名 + 密码  -->
                    <el-form-item label="用户名" prop="username">
                        <el-input maxlength="5" placeholder="请输入用户名" v-model="ruleForm.username"></el-input>
                    </el-form-item>
                    <el-form-item label="密码" prop="password">
                        <el-input 
                            type="password"
                            v-model="ruleForm.password"
                            autocomplete="off"
                            placeholder="请输入密码"
                        ></el-input>
                    </el-form-item>
                    <!--  提交表单  -->
                    <el-form-item>
                    <el-button type="primary" @click="submitForm('ruleForm')">提交</el-button>
                    <el-button @click="resetForm('ruleForm')">重置</el-button>
                    </el-form-item>

                </el-form>
            </el-dialog>
        </div>
    </div>
</template>


<script>


export default {
    data() {
        return {
            isLogin: false,
            authorName: "paperClub",
            loginType: 'register',
            dialogVisible: false,
            ruleForm: { username: "",  password: "" },
            rules: {
                username: [
                            { required: true, message: '请输入用户名', trigger: 'blur' },
                          ],
                password: [
                            { required: true, message: '请输入密码', trigger: 'blur' },
                            { min: 3, max: 5, message: '密码格式错误', trigger: 'blur'}
                          ],
                },
            }
    },

    methods: {

        login(loginType){ // 登录、注册
            this.loginType = loginType
            this.dialogVisible = true
        },


        submitForm(formName) { // 提交表单
            // console.log("submitForm: ", this.ruleForm)
            this.$refs[formName].validate((valid) => {
                if (valid) {
                    this.authorName = this.username,
                    this.$message({
                        message: '提交成功！',
                        center: true,
                        type: 'success'
                    })
                    return true;

                } else {
                    this.$message({
                        message: '密码长度应为 3 ~ 5 !',
                        center: true,
                        type: 'warning'
                    })
                    return false;
                }
            });
        },

        resetForm(formName) { // 重置表单
            this.$refs[formName].resetFields();
      },

     
        
    }
}

</script>


<style  scoped>
.header-wrapper {
    height: 60px;
    border-bottom: 1px solid rgb(209, 206, 211);
    display: flex;
    align-items: center;
    position: fixed;
    top: 0;
    background: rgb(255, 253, 254);
    width: 100%; 
}


.header-main {
    width: 1080px;
    margin: 0 auto;
        display: flex;
    justify-content: space-between;
}

.left-box {
    display: flex;
    align-items: center;
}

.img {
    border-radius: 40px;
    margin-right: 20px;
}

.blog-title {
    color: rgb(38, 38, 39);
    margin-right: 100px;
}

.article-cat-box{
    display: flex;
    color: gray;
    align-content: center;
}

.cat-item {
    margin-right: 30px;
    cursor: pointer;
    
}

.right-box {
    display: flex;
    align-content: center;
    color: #4548e7;
}

.login {
    margin-right: 10px;
    cursor: pointer;
}

.register {
    cursor: pointer;
}



</style>