import { useState, useEffect } from 'react';
import { Search, Mail, Phone, Eye } from 'lucide-react';
import { Input } from '../../components/ui/input';
import { Card } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { toast } from 'sonner';

interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  total_orders: number;
  total_spent: string;
  created_at: string;
}

export default function AdminCustomers() {
  const [searchQuery, setSearchQuery] = useState('');
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchCustomers();
  }, []);

  const fetchCustomers = async () => {
    try {
      const email = localStorage.getItem('adminEmail') || '';
      const password = localStorage.getItem('adminPassword') || '';
      
      const response = await fetch('/api/admin/customers', {
        headers: {
          'x-admin-email': email,
          'x-admin-password': password,
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCustomers(data);
      } else {
        toast.error('Failed to load customers from Neon database');
      }
    } catch (error) {
      toast.error('Failed to fetch customers');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredCustomers = customers.filter(customer =>
    customer.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    customer.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (customer.phone && customer.phone.includes(searchQuery))
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-serif italic text-primary font-bold">Customers</h1>
        <p className="text-muted-foreground mt-2">
          View and manage registered customers stored in Neon DB
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
        <Card className="p-4 border-l-4 border-l-primary/60">
          <p className="text-sm text-muted-foreground">Registered Customers</p>
          <p className="text-2xl mt-1 font-semibold">{customers.length}</p>
        </Card>
        <Card className="p-4 border-l-4 border-l-primary/60">
          <p className="text-sm text-muted-foreground">Total Orders</p>
          <p className="text-2xl mt-1 font-semibold">
            {customers.reduce((sum, c) => sum + Number(c.total_orders || 0), 0)}
          </p>
        </Card>
        <Card className="p-4 border-l-4 border-l-primary/60">
          <p className="text-sm text-muted-foreground">Total Revenue</p>
          <p className="text-2xl mt-1 font-semibold">
            ${customers.reduce((sum, c) => sum + Number(c.total_spent || 0), 0).toFixed(2)}
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
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-muted-foreground">
                    Loading customers from Neon...
                  </td>
                </tr>
              ) : filteredCustomers.map((customer) => (
                <tr key={customer.id} className="hover:bg-muted/30">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-primary/10 text-primary font-medium">
                        {customer.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="font-medium">{customer.name}</p>
                        <p className="text-xs text-muted-foreground">ID: {customer.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="h-3 w-3 text-muted-foreground" />
                        <span>{customer.email}</span>
                      </div>
                      {customer.phone && (
                        <div className="flex items-center gap-2 text-sm">
                          <Phone className="h-3 w-3 text-muted-foreground" />
                          <span>{customer.phone}</span>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-medium text-sm px-2 py-1 bg-muted rounded">{customer.total_orders || 0}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-medium text-green-700 bg-green-50 px-2 py-1 rounded">
                      ${Number(customer.total_spent || 0).toFixed(2)}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-sm text-muted-foreground">
                      {new Date(customer.created_at).toLocaleDateString()}
                    </span>
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

      {!isLoading && filteredCustomers.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">No registered customers found in Neon DB.</p>
        </div>
      )}
    </div>
  );
}
