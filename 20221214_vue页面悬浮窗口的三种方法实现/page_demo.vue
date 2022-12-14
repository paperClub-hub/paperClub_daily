<template>
    <div > 
        <!-- 悬浮方案1 -->
        <div v-if='show_DragDiv1' class="realTranslationInfos" v-drag>
            <div class="dragdiv_header">
                <div class="RealtranslationBox">
                    <!-- <el-button class="el-icon-circle-close"  @click="close_dragDiv()"></el-button> -->
                    <a class="el-icon-circle-close"  @click="close_dragDiv()"></a>
                    <img draggable="false" @click="allconversationclik" :src=wx_gzh alt="" width="180ex" >
                </div>
            </div>
        </div>


        <!-- 悬浮方案2 -->
        <div ref="dragDiv" class="float-drag-button">
            <span> PaperClub 
                <img src="@/assets/img/wx.jpg" width="100px">
            </span>
        </div>



        <!-- 悬浮方案3 -->
        <div class="div1" @mousemove="showDiv1()" @mouseout="hideDiv1()">
            <div class="div_header">
            <i class="el-icon-circle-close"></i>
            PaperClub </div>
            
            <div class="div_main" id="div_main"> </div>
        </div>

    </div>
    
</template>



<script>
import xxx from './drag.js';



export default {
    

    data() {
        return {
            show_DragDiv1: true,
            wx_gzh: require("../assets/img/wx.jpg")
            };
        },


    components: {
      // mytest
        },


    mounted() {
        
        this.$nextTick(() => {
      // 获取DOM元素
      let dragDiv = this.$refs.dragDiv;
      // 缓存 clientX clientY 的对象: 用于判断是点击事件还是移动事件
      let clientOffset = {};
      // 绑定鼠标按下事件
      dragDiv.addEventListener("mousedown", (event) => {
        let offsetX = dragDiv.getBoundingClientRect().left; // 获取当前的x轴距离
        let offsetY = dragDiv.getBoundingClientRect().top; // 获取当前的y轴距离
        let innerX = event.clientX - offsetX; // 获取鼠标在方块内的x轴距
        let innerY = event.clientY - offsetY; // 获取鼠标在方块内的y轴距
        console.log(offsetX, offsetY, innerX, innerY);
        // 缓存 clientX clientY
        clientOffset.clientX = event.clientX;
        clientOffset.clientY = event.clientY;
        // 鼠标移动的时候不停的修改div的left和top值
        document.onmousemove = function(event) {
          dragDiv.style.left = event.clientX - innerX + "px";
          dragDiv.style.top = event.clientY - innerY + "px";
          // dragDiv 距离顶部的距离
          let dragDivTop = window.innerHeight - dragDiv.getBoundingClientRect().height;
          // dragDiv 距离左部的距离
          let dragDivLeft = window.innerWidth - dragDiv.getBoundingClientRect().width;
          // 边界判断处理
          // 1、设置左右不能动
          dragDiv.style.left = dragDivLeft + "px";
          // 2、超出顶部处理
          if (dragDiv.getBoundingClientRect().top <= 0) {
            dragDiv.style.top = "0px";
          }
          // 3、超出底部处理
          if (dragDiv.getBoundingClientRect().top >= dragDivTop) {
            dragDiv.style.top = dragDivTop + "px";
          }
        };
        // 鼠标抬起时，清除绑定在文档上的mousemove和mouseup事件；否则鼠标抬起后还可以继续拖拽方块
        document.onmouseup = function() {
          document.onmousemove = null;
          document.onmouseup = null;
        };
      }, false);
      // 绑定鼠标松开事件
      dragDiv.addEventListener('mouseup', (event) => {
        let clientX = event.clientX;
        let clientY = event.clientY;
        if (clientX === clientOffset.clientX && clientY === clientOffset.clientY) {
          console.log('click 事件');
        } else {
          console.log('drag 事件');
        }
      })
    });


    },

    computed: {
        noMore () {
        return this.count >= 3
        },
      disabled () {
        return this.loading || this.noMore
      }
    },


    methods: {
        showDiv1(){
            var d1 =  document.getElementById('div_main');
            d1.style.cssText = 'display:block;'
        },
        hideDiv1(){
            var d1 =  document.getElementById('div_main');
            d1.style.cssText = 'display:none;'
        },
        
        close_dragDiv(){ 
            console.log("方法1：关闭浮窗")
            this.show_DragDiv1 = false

        },
        allconversationclik(){
          console.log("方法1：点击")
        },

    }
};
</script>



<style scoped>

/* 悬浮框显示1 */

.dragdiv_header{
  height: 300px;
  width: 240px;
  /* border: 1px solid; */
  /* background-color: rgb(248, 248, 250); */

}

.realTranslationInfos {
      width: 100px;
      height: 100px;
      background: rgb(251, 249, 249);
      position: absolute;
      bottom: 88px;
      right: 20px;
      bottom: 122px;
     right: -30px;
}
      .translationContent {
        min-height: 100px;
        line-height: 23px;
        width: 338px;
        padding: 18px 74px 19px 19px;
        background: #fafafb;
        opacity: 0.80;
        border-radius: 12px;
        color: #fff;
        position: absolute;
        right: 58px;
        bottom: 22px;
        z-index: 999;
        
      }
      .RealtranslationBox {
        display: flex;
        align-items: center;
        position: absolute;
        right: 2px;
        bottom: 5px;
        z-index: 999;
        cursor: move;
    }
    /* .img {
        cursor: pointer;
    } */
    
/* 2 */
.float-drag-button {
  position: absolute;
  right: 0;
  top: 40%;
  z-index: 6666;
  padding: 13px;
  width: 100px;
  opacity: 1;
  background-color: rgb(225, 138, 138);
  border-radius: 8px 0px 0px 8px;
  box-shadow: 0px 2px 15px 0px rgba(32, 91, 159, 0.15);
  cursor: move;
}


/* 3 */
.div1 {
  height: 10px;
  width: 100px;
  border: 1px solid;
  position: fixed;
  top: 50%;
  right: 0px;
  cursor: pointer;
}

.div_header {
  width: 300px;
  /* height: 50px; */
  /* border: 1px solid; */
  /* line-height: 50px; */
  text-align: center;
  background-color: #09ba2f;
  background-image: linear-gradient(62deg, #059473 0%, #f2f1f4 100%);

}
.div_main{
  height: 100px;
  width: 100px;
  /* margin-top: 10px; */
  background-image: url('../assets/img/wx.jpg');
  background-size: 100px 100px;
  display: none;
}

</style>
