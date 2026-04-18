import { createRouter, createWebHistory } from ''vue-router'
import HomeView from '../views/HomeView.vue'
import MovieDetail form '../views/MovieDetail.vue'

const routes = [
    {
        path: '/',
        component: HomeView
    },

    {
        path: '/film/:id',
        component: MovieDetail
    }
]

const router = createRouter(
    {
        history: createWebHistory().
        routes
    }
)

export default router