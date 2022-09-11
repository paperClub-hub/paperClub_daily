<template>
    <div class="footer-wrapper"> 
        <a onclick="window.open('http://www.infersite.com' )" style="cursor:hand"> 版权信息 @ paperClub </a>
    </div>
</template>

<script>
export default {
    name: "Footer",
};

</script>

<style>
.footer-wrapper {
    height: 50px;
    border-top: 1px solid rgb(232, 230, 234);
    color: rgb(54, 6, 244);
    text-align: center;
    line-height: 50px;
    cursor:pointer;
}

.footer-wrapper:hover{
    background-color: #efedf1;
}
</style>