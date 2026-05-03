<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
    notation: number;

}>();

const emit = defineEmits ([
    "rate"
]);

const currentNotation = ref(0);
const finalNotation=ref(0);

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
<div class="starsContainer">
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
        @click="() => { finalNotation = currentNotation; $emit('rate', currentNotation) }"
    >
        <span 
        class="star"
        :class="getDisplayValue(star)"
        >★</span>
    </div>
    
</div>
<div class="note">{{ finalNotation }}★</div>
</div>
</template>
