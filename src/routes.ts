import { createBrowserRouter } from "react-router";
import StoreFront from "./pages/StoreFront";
import AdminLayout from "./pages/admin/AdminLayout";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminProducts from "./pages/admin/AdminProducts";
import AdminOrders from "./pages/admin/AdminOrders";
import AdminCustomers from "./pages/admin/AdminCustomers";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: StoreFront,
  },
  {
    path: "/admin",
    Component: AdminLayout,
    children: [
      { index: true, Component: AdminDashboard },
      { path: "products", Component: AdminProducts },
      { path: "orders", Component: AdminOrders },
      { path: "customers", Component: AdminCustomers },
    ],
  },
]);
