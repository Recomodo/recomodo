<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
    notation: number;
}>();

const emit = defineEmits ([
    "update:notation"
]);

const currentNotation = ref(0);

function changeNotation(value: number) {
    emit("update:notation", value);
}

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
        v-for="star in 5"
        :key="star"
        class="star-wrapper"
        @mousemove="(e) => {
            const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
            const isHalf = e.clientX - rect.left <rect.width / 2;
            currentNotation = isHalf ? star - 0.5 : star;  
        }"
        @mouseleave="currentNotation = 0"
        @click="changeNotation(currentNotation)"
    >
        <span class="starBase">★</span>
        <span v-if="getDisplayValue(star) === 'full'" class="starFull">★</span>
        <span v-else-if="getDisplayValue(star) === 'half'" class="starHalf">★</span>
        
   
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

/*
.star {
    color: #ccc;
    transition:  0.2s;
}

.star.active {
    color: #ffcc00;
    transform: scale(1.1);
}
    */

.star-wrapper {
    position: relative;
    width: 32px;
    height: 32px;
}

.star {
    position: absolute;
    top: 0;
    left: 0;
}

.base {
    color: #444;
}

.full {
    color: #ffcc00;
}
.half {
    color: #ffcc00;
    width: 50%;
    overflow: hidden;
    display: inline-block;
}
</style>