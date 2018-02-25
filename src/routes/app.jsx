import Dashboard from '../views/Dashboard/Dashboard';
import TableList from '../views/TableList/TableList';

const appRoutes = [
    { path: "/dashboard", name: "Dashboard", icon: "pe-7s-graph", component: Dashboard },
    { path: "/table", name: "Issues", icon: "pe-7s-note2", component: TableList },
    { redirect: true, path:"/", to:"/dashboard", name: "Dashboard" }
];

export default appRoutes;
