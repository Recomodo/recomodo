<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
    notation: number;
}>();

const emit = defineEmits ([
    "rate"
]);

const currentNotation = ref(0);

function getDisplayValue(star: number) {
    const displayValue = currentNotation.value || props.notation;

    if (displayValue >= star) {
        return 'full';
    }
    if (displayValue >= star - 0.5) {
        return 'half';
    }
    return 'empty';
}
</script>

<template>
<div class="stars">
    <div
        v-for="star in 10"
        :key="star"
        class="star-wrapper"
        @mousemove="(e) => {
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
            const isHalf = e.clientX - rect.left <rect.width / 2;
            currentNotation = isHalf ? star - 0.5 : star;  
        }"
        @mouseleave="currentNotation = 0"
        @click="$emit('rate' , star)"
    >
        <span 
         class="star"
         :class="getDisplayValue(star)"
        > 
            ★
        </span>
        
   
    </div>
</div>
</template>

<style scoped>
.stars {
    display: flex;
    gap: 6px;
    font-size: 2rem;
    cursor: pointer;
}

.star-wrapper {
    position: relative;
    width: 32px;
    height: 32px;
}

.star {
    position: absolute;
    top: 0;
    left: 0;
    color:white;
    transition: 0.2s;
}

.full {
    color: rgb(222, 106, 222);
}
.half {
    color: rgb(222, 106, 222);
    width: 50%;
    overflow: hidden;
    display: inline-block;
}
</style>