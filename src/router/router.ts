import { createRouter, createWebHistory} from "vue-router"
import HomeView from "@/views/HomeView.vue"

const routes = [
    {
        path:"/movie/details/:id",
        name:"details",
        component: () => import("../views/DetailsPage.vue"),
        props: true,
    },
    {
        path:"/recommendations",
        name:"recommendations",
        component: () => import("../views/RecommandationPage.vue"),
    },
    {
        path:"/profile",
        name:"profile",
        component: () => import("../views/ProfilePage.vue"),
    },
    {
        path:"/",
        name:"home",
        component: HomeView,
    }
]


const router = createRouter ({
  history: createWebHistory(),
  routes,
})

export default router