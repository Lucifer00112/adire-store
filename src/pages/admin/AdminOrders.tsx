import { useState } from 'react';
import { Search, Eye, Package, Truck, CheckCircle } from 'lucide-react';
import { Input } from '../../components/ui/input';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';

const mockOrders = [
  {
    id: 'ORD-001',
    customer: 'Adebayo Oluwaseun',
    email: 'adebayo@example.com',
    total: 89.99,
    status: 'delivered',
    date: '2025-03-08',
    items: 1,
  },
  {
    id: 'ORD-002',
    customer: 'Chioma Nwankwo',
    email: 'chioma@example.com',
    total: 125.50,
    status: 'processing',
    date: '2025-03-08',
    items: 2,
  },
  {
    id: 'ORD-003',
    customer: 'Ibrahim Mohammed',
    email: 'ibrahim@example.com',
    total: 65.99,
    status: 'shipped',
    date: '2025-03-07',
    items: 1,
  },
  {
    id: 'ORD-004',
    customer: 'Funmilayo Adeyemi',
    email: 'funmi@example.com',
    total: 198.75,
    status: 'pending',
    date: '2025-03-07',
    items: 3,
  },
  {
    id: 'ORD-005',
    customer: 'Emeka Okafor',
    email: 'emeka@example.com',
    total: 52.99,
    status: 'delivered',
    date: '2025-03-06',
    items: 1,
  },
  {
    id: 'ORD-006',
    customer: 'Blessing Okoro',
    email: 'blessing@example.com',
    total: 156.97,
    status: 'processing',
    date: '2025-03-06',
    items: 3,
  },
  {
    id: 'ORD-007',
    customer: 'Tunde Bakare',
    email: 'tunde@example.com',
    total: 45.99,
    status: 'shipped',
    date: '2025-03-05',
    items: 1,
  },
  {
    id: 'ORD-008',
    customer: 'Amina Bello',
    email: 'amina@example.com',
    total: 210.50,
    status: 'pending',
    date: '2025-03-05',
    items: 4,
  },
];

const statusConfig = {
  pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-700', icon: Package },
  processing: { label: 'Processing', color: 'bg-blue-100 text-blue-700', icon: Package },
  shipped: { label: 'Shipped', color: 'bg-purple-100 text-purple-700', icon: Truck },
  delivered: { label: 'Delivered', color: 'bg-green-100 text-green-700', icon: CheckCircle },
};

export default function AdminOrders() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  const filteredOrders = mockOrders.filter(order => {
    const matchesSearch = 
      order.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.customer.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.email.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1>Orders</h1>
        <p className="text-muted-foreground mt-1">
          Manage and track customer orders
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search orders, customers..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="processing">Processing</SelectItem>
            <SelectItem value="shipped">Shipped</SelectItem>
            <SelectItem value="delivered">Delivered</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Orders Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium">Order ID</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Customer</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Date</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Items</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Total</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-6 py-3 text-right text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredOrders.map((order) => {
                const StatusIcon = statusConfig[order.status].icon;
                return (
                  <tr key={order.id} className="hover:bg-muted/30">
                    <td className="px-6 py-4">
                      <p className="font-medium">{order.id}</p>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium">{order.customer}</p>
                        <p className="text-sm text-muted-foreground">{order.email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm">{order.date}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm">{order.items} item{order.items > 1 ? 's' : ''}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium">${order.total}</span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs ${statusConfig[order.status].color}`}>
                          <StatusIcon className="h-3 w-3" />
                          {statusConfig[order.status].label}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center justify-end gap-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4 mr-2" />
                          View
                        </Button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </Card>

      {filteredOrders.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No orders found matching your criteria.</p>
        </div>
      )}
    </div>
  );
}
