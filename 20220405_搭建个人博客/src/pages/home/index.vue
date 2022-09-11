<template>
    <div class="page-home">
        <Article></Article>
        <Article></Article>
        <Article></Article>
        <Article></Article>
        <Article></Article>
        <Article></Article>
    </div>
</template>



<script>

import Article from './component';
export default {
    components: {
        Article,
    },
    
};
</script>

<style >
.page-home{
    width: 800px;
    margin: 51px auto;
}
</style>