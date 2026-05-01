<script setup lang="ts">
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

<style scoped>
    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      margin: 4rem auto 2rem auto;
      gap: 2rem;
      padding: 1rem 2rem;
      width: fit-content;
      background: #15001d;
      border-radius: 12px;
      backdrop-filter: blur(10px);
      color: white;
      margin-top: auto;
    }

    .pagination button {
      padding: 0.5rem 1rem;
      background: #7a2a8a;
      color: white;
      border: none;
      cursor: pointer;
    }

    .pagination button:disabled {
      background: #ccc;
      cursor: not-allowed;
    }
</style>

