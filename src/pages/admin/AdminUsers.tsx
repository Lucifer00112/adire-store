import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../components/ui/table';
import { toast } from 'sonner';
import { UserPlus, Calendar } from 'lucide-react';

interface AdminUser {
  id: number;
  email: string;
  password: string; // ONLY BECAUSE USER EXPLICITLY REQUESTED
  created_at: string;
}

export default function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const email = localStorage.getItem('adminEmail') || '';
      const password = localStorage.getItem('adminPassword') || '';
      
      const response = await fetch('/api/admin/users', {
        headers: {
          'x-admin-email': email,
          'x-admin-password': password,
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else {
        toast.error('Failed to authenticate with Neon database');
      }
    } catch (error) {
      toast.error('Failed to fetch admin users');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-serif italic text-primary font-bold">Administrators</h1>
        <p className="text-muted-foreground mt-2">Manage restricted access Neon database admin accounts.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserPlus className="h-5 w-5 text-primary" />
            Registered Admins
          </CardTitle>
          <CardDescription>
            Admin email and password records stored securely in PostgreSQL.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Email</TableHead>
                  <TableHead>Password</TableHead>
                  <TableHead className="text-right">Registered On</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center py-8">Loading admins...</TableCell>
                  </TableRow>
                ) : users.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center text-muted-foreground py-8">
                      No admins found in the Neon database. Create one from the login screen.
                    </TableCell>
                  </TableRow>
                ) : (
                  users.map((user) => (
                    <TableRow key={user.id}>
                      <TableCell className="font-medium">{user.email}</TableCell>
                      <TableCell>
                        <span className="font-mono text-xs bg-muted px-2 py-1 rounded border overflow-hidden truncate max-w-[200px] inline-block">{user.password}</span>
                      </TableCell>
                      <TableCell className="text-right text-muted-foreground flex items-center justify-end gap-2">
                        <Calendar className="h-4 w-4" />
                        {new Date(user.created_at).toLocaleDateString()}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
