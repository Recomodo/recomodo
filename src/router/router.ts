import { createRouter, createWebHistory} from "vue-router"
import RecommandationPage from "../views/RecommandationPage.vue"

const routes = [
    {
        path:'/profile',
        name:"profile",
        component: () => import("../views/ProfilePage.vue"),
    },
    {
        path:"/details/:id?",
        name:"details",
        component: () => import("../views/DetailsPage.vue"),
    },
    {
        path:"/",
        name:"recommendations",
        component: RecommandationPage,
    },
    {
        path:"/first-sign-in",
        name:"first-sign-in",
        component: () => import("../views/FirstSigninPage.vue"),
    }
]

const router = createRouter ({
  history: createWebHistory(),
  routes,
})

export default router