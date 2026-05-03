<script setup lang="ts">
import '@/assets/CssPagination.css';

const props = defineProps<{
    currentPage: number;
}>();

const emit = defineEmits ([
    "page-changed"
]);

function changePage(page: number) {
    if (page >= 1) {
        emit("page-changed", page);
    }
}
</script>

<template>
    <div class="pagination">
      <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1">Previous</button>
      <span>Page {{ currentPage }}</span>
      <button @click="changePage(currentPage + 1)">Next</button>
    </div>
</template>

