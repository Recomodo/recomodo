import { createRouter, createWebHistory} from "vue-router"
import HomeView from "../views/HomeView.vue"

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
        props: true,
    },
    {
        path:"/Recommendations",
        name:"recommendations",
        component: () => import("../views/RecommandationPage.vue"),
    },
    {
        path:"/first-sign-in",
        name:"first-sign-in",
        component: () => import("../views/FirstSigninPage.vue"),
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