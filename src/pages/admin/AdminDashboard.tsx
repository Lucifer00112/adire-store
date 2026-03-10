import { Card } from '../../components/ui/card';
import { DollarSign, Package, ShoppingCart, Users, TrendingUp, TrendingDown } from 'lucide-react';

const stats = [
  {
    name: 'Total Revenue',
    value: '$12,345',
    change: '+12.5%',
    trend: 'up',
    icon: DollarSign,
  },
  {
    name: 'Total Orders',
    value: '156',
    change: '+8.2%',
    trend: 'up',
    icon: ShoppingCart,
  },
  {
    name: 'Products',
    value: '48',
    change: '+3',
    trend: 'up',
    icon: Package,
  },
  {
    name: 'Customers',
    value: '234',
    change: '+15.3%',
    trend: 'up',
    icon: Users,
  },
];

const recentOrders = [
  { id: 'ORD-001', customer: 'Adebayo Oluwaseun', amount: 89.99, status: 'delivered', date: '2025-03-08' },
  { id: 'ORD-002', customer: 'Chioma Nwankwo', amount: 125.50, status: 'processing', date: '2025-03-08' },
  { id: 'ORD-003', customer: 'Ibrahim Mohammed', amount: 65.99, status: 'shipped', date: '2025-03-07' },
  { id: 'ORD-004', customer: 'Funmilayo Adeyemi', amount: 198.75, status: 'pending', date: '2025-03-07' },
  { id: 'ORD-005', customer: 'Emeka Okafor', amount: 52.99, status: 'delivered', date: '2025-03-06' },
];

const topProducts = [
  { name: 'Traditional Agbada Set', sales: 45, revenue: '$4,049.55' },
  { name: 'Adire Kaftan - Women', sales: 38, revenue: '$2,127.62' },
  { name: 'Men\'s Adire Senator Wear', sales: 32, revenue: '$1,695.68' },
  { name: 'Adire Wrapper & Blouse', sales: 28, revenue: '$1,847.72' },
  { name: 'Modern Adire Jumpsuit', sales: 24, revenue: '$1,655.76' },
];

export default function AdminDashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1>Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Welcome back! Here's what's happening with your store today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          const TrendIcon = stat.trend === 'up' ? TrendingUp : TrendingDown;
          return (
            <Card key={stat.name} className="p-6">
              <div className="flex items-center justify-between">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
                <div className={`flex items-center gap-1 text-sm ${
                  stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                }`}>
                  <TrendIcon className="h-4 w-4" />
                  <span>{stat.change}</span>
                </div>
              </div>
              <div className="mt-4">
                <p className="text-sm text-muted-foreground">{stat.name}</p>
                <p className="text-2xl mt-1">{stat.value}</p>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Orders */}
        <Card className="p-6">
          <h3 className="mb-4">Recent Orders</h3>
          <div className="space-y-4">
            {recentOrders.map((order) => (
              <div key={order.id} className="flex items-center justify-between py-3 border-b last:border-0">
                <div className="space-y-1">
                  <p className="font-medium">{order.id}</p>
                  <p className="text-sm text-muted-foreground">{order.customer}</p>
                </div>
                <div className="text-right space-y-1">
                  <p className="font-medium">${order.amount}</p>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    order.status === 'delivered' ? 'bg-green-100 text-green-700' :
                    order.status === 'processing' ? 'bg-blue-100 text-blue-700' :
                    order.status === 'shipped' ? 'bg-purple-100 text-purple-700' :
                    'bg-yellow-100 text-yellow-700'
                  }`}>
                    {order.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Top Products */}
        <Card className="p-6">
          <h3 className="mb-4">Top Products</h3>
          <div className="space-y-4">
            {topProducts.map((product, index) => (
              <div key={product.name} className="flex items-center justify-between py-3 border-b last:border-0">
                <div className="flex items-center gap-3">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary/10 text-primary font-medium">
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{product.name}</p>
                    <p className="text-xs text-muted-foreground">{product.sales} sales</p>
                  </div>
                </div>
                <p className="font-medium">{product.revenue}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
