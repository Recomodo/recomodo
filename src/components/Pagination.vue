<script setup lang="ts">
const props = defineProps<{
    totalPages: number;
    currentPage: number;
}>();

const emit = defineEmits ([
    "page-changed"
]);

function changePage(page: number) {
    if (page >= 1 && page <= props.totalPages) {
        emit("page-changed", page);
    }
}
</script>

<template>
    <div class="pagination">
        <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1">Précédent</button>
        <span>Page {{ currentPage }} sur {{ totalPages }}</span>
        <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">Suivant</button>
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

        background: rgba(0, 0, 0, 0.2);
        border-radius: 12px;
        backdrop-filter: blur(10px);
        color: white;

        margin-top: auto;
    }

    .pagination button {
        padding: 0.5rem 1rem;
        background: #007bff;
        color: white;
        border: none;
        cursor: pointer;
    }

    .pagination button:disabled {
        background: #ccc;
        cursor: not-allowed;
    }
</style>

