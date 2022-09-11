<template>
    <div class="com-article">
        <div class="article-left">
            <div>
                <div class="info">
                    <span> sum </span>
                    <span class="publish-time">2022.03.20</span>
                    <span class="cat"> element-ui</span>
                </div>
                <div class="title"> 新手如何搭建个人网站 </div>
                <div class="count">
                    <span class="likes">喜欢 5</span>
                    <span>阅读 10</span>
                </div>
            </div>
        </div>
        <div class="article-right">
            <img src="../../../assets/avatar.png" width="80px">
        </div>
    </div>
</template>


<script>

export default ({
   
})
</script>

<style >
.com-article {
    padding: 20px;
    background-color: #fff;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
}

.info {
    color: gray;
    font-size: 16px;
}

.publish-time {
    margin: 0 15px;
}

.cat {
    color: #4548e7;
    cursor: pointer;
}

.title {
    font-weight: bold;
    font-size:20px;
    margin: 10px 0;
    cursor: pointer;
}

.likes {
    margin-right: 10px;
}
        
.count {
    color: gray;
}






</style>
