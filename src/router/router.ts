import { createRouter, createWebHistory} from "vue-router"
import HomePage from "../views/HomePage.vue"

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
        component: HomePage,
    }
]


const router = createRouter ({
  history: createWebHistory(),
  routes,
})

export default router