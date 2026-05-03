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
    {{ finalNotation }}
</div>
</template>

<style scoped>
.stars {
    display: flex;
    font-size: 1.6rem;
    cursor: pointer;
}

.star-wrapper {
    position: relative;
    width: 22px;
}

.star {
    position: absolute;
    color:white;
    transition: 0.2s;
}

.full {
    color: #f5c518;
}
.half {
    color: #f5c518;
    width: 50%;
    overflow: hidden;
    display: inline-block;
}

</style>