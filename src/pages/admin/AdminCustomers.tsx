import { useState } from 'react';
import { Search, Mail, Phone, Eye } from 'lucide-react';
import { Input } from '../../components/ui/input';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';

const mockCustomers = [
  {
    id: '1',
    name: 'Adebayo Oluwaseun',
    email: 'adebayo@example.com',
    phone: '+234 801 234 5678',
    totalOrders: 12,
    totalSpent: 1289.45,
    joinDate: '2024-11-15',
  },
  {
    id: '2',
    name: 'Chioma Nwankwo',
    email: 'chioma@example.com',
    phone: '+234 802 345 6789',
    totalOrders: 8,
    totalSpent: 845.20,
    joinDate: '2024-12-03',
  },
  {
    id: '3',
    name: 'Ibrahim Mohammed',
    email: 'ibrahim@example.com',
    phone: '+234 803 456 7890',
    totalOrders: 15,
    totalSpent: 1567.80,
    joinDate: '2024-10-22',
  },
  {
    id: '4',
    name: 'Funmilayo Adeyemi',
    email: 'funmi@example.com',
    phone: '+234 804 567 8901',
    totalOrders: 6,
    totalSpent: 678.90,
    joinDate: '2025-01-08',
  },
  {
    id: '5',
    name: 'Emeka Okafor',
    email: 'emeka@example.com',
    phone: '+234 805 678 9012',
    totalOrders: 9,
    totalSpent: 923.50,
    joinDate: '2024-11-28',
  },
  {
    id: '6',
    name: 'Blessing Okoro',
    email: 'blessing@example.com',
    phone: '+234 806 789 0123',
    totalOrders: 11,
    totalSpent: 1134.75,
    joinDate: '2024-12-15',
  },
  {
    id: '7',
    name: 'Tunde Bakare',
    email: 'tunde@example.com',
    phone: '+234 807 890 1234',
    totalOrders: 4,
    totalSpent: 432.80,
    joinDate: '2025-02-01',
  },
  {
    id: '8',
    name: 'Amina Bello',
    email: 'amina@example.com',
    phone: '+234 808 901 2345',
    totalOrders: 13,
    totalSpent: 1445.60,
    joinDate: '2024-10-05',
  },
];

export default function AdminCustomers() {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredCustomers = mockCustomers.filter(customer =>
    customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    customer.phone.includes(searchQuery)
  );

  return (
    <div className="space-y-6">
      <div>
        <h1>Customers</h1>
        <p className="text-muted-foreground mt-1">
          View and manage your customer base
        </p>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search customers..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Total Customers</p>
          <p className="text-2xl mt-1">{mockCustomers.length}</p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Total Orders</p>
          <p className="text-2xl mt-1">
            {mockCustomers.reduce((sum, c) => sum + c.totalOrders, 0)}
          </p>
        </Card>
        <Card className="p-4">
          <p className="text-sm text-muted-foreground">Total Revenue</p>
          <p className="text-2xl mt-1">
            ${mockCustomers.reduce((sum, c) => sum + c.totalSpent, 0).toFixed(2)}
          </p>
        </Card>
      </div>

      {/* Customers Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium">Customer</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Contact</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Orders</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Total Spent</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Join Date</th>
                <th className="px-6 py-3 text-right text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredCustomers.map((customer) => (
                <tr key={customer.id} className="hover:bg-muted/30">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-medium">
                        {customer.name.charAt(0)}
                      </div>
                      <div>
                        <p className="font-medium">{customer.name}</p>
                        <p className="text-sm text-muted-foreground">ID: {customer.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="h-3 w-3 text-muted-foreground" />
                        <span>{customer.email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Phone className="h-3 w-3 text-muted-foreground" />
                        <span>{customer.phone}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-medium">{customer.totalOrders}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-medium">${customer.totalSpent.toFixed(2)}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm">{customer.joinDate}</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end">
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        View
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {filteredCustomers.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No customers found matching your criteria.</p>
        </div>
      )}
    </div>
  );
}
