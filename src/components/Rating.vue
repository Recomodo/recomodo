<script lang="ts" setup>
import {ref} from 'vue'

const props= defineProps<{
    modelValue:number
}>()

const emit= defineEmits<{
    (e: 'update:modelValue', value:number):void
}>()

const hover=ref(0)

const update=(value:number)=>{
    emit('update:modelValue',value)
}
</script>


<template>
    <div class="rating">
       <span v-for="n in 10" :key="n" class="star" 
       :class="{active : n<=(hover || modelValue)}"
       @click="update(n)"
       @mouseover="hover=n"
       @mouseleave="hover=0">
       <font-awesome-icon icon="fa-solid fa-star" size="xs" />
       </span>

    </div>
    </template>

<style scoped>
.star {
  cursor: pointer;
  color: #ccc;
  font-size: 1.5rem;
  transition: 0.2s;
}

.star.active {
  color: rgb(222, 106, 222);
  transform: scale(1.1);
}
</style>