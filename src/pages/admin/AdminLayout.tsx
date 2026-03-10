import { Outlet, Link, useLocation } from 'react-router';
import { LayoutDashboard, Package, ShoppingCart, Users, Menu, X, LockKeyhole } from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';

const navigation = [
  { name: 'Dashboard', href: '/admin', icon: LayoutDashboard },
  { name: 'Products', href: '/admin/products', icon: Package },
  { name: 'Orders', href: '/admin/orders', icon: ShoppingCart },
  { name: 'Customers', href: '/admin/customers', icon: Users },
];

export default function AdminLayout() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);

  useEffect(() => {
    const savedPassword = localStorage.getItem('adminPassword');
    if (savedPassword) {
      verifyPassword(savedPassword);
    }
  }, []);

  const verifyPassword = async (pass: string) => {
    setIsVerifying(true);
    try {
      const response = await fetch('/api/admin/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-admin-password': pass
        }
      });

      if (response.ok) {
        localStorage.setItem('adminPassword', pass);
        setIsAuthenticated(true);
        toast.success('Welcome to the Admin Vault');
      } else {
        localStorage.removeItem('adminPassword');
        setIsAuthenticated(false);
        if (password) toast.error('Incorrect password');
      }
    } catch (error) {
      console.error('Verification error:', error);
      toast.error('Could not connect to server');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    verifyPassword(password);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#FDF9F1] flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <div className="flex justify-center">
            <div className="h-16 w-16 bg-[#4A0080]/10 rounded-full flex items-center justify-center">
              <LockKeyhole className="h-8 w-8 text-[#4A0080]" />
            </div>
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900 tracking-tight font-serif italic text-primary">
            Admin Vault
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Welcome back. Please enter your master password to access the boutique management dashboard.
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow-xl sm:rounded-2xl sm:px-10 border border-[#4A0080]/10">
            <form className="space-y-6" onSubmit={handleLogin}>
              <div>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-[#4A0080] focus:border-[#4A0080] sm:text-sm transition-colors duration-200"
                />
              </div>

              <div>
                <Button
                  type="submit"
                  disabled={isVerifying}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-[#4A0080] hover:bg-[#3A0060] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4A0080] transition-all duration-200 disabled:opacity-70"
                >
                  {isVerifying ? 'Verifying Signature...' : 'Enter Dashboard'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-full w-64 bg-card border-r transition-transform duration-300
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex items-center justify-between p-6 border-b">
          <h1 className="font-serif italic text-primary text-xl font-bold">EURYTEXTILES</h1>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="p-4 space-y-2">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                  ${isActive
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-accent text-foreground'
                  }
                `}
              >
                <Icon className="h-5 w-5" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 left-0 right-0 p-4 border-t space-y-2">
          <Button variant="ghost" className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10" onClick={() => { localStorage.removeItem('adminPassword'); setIsAuthenticated(false); }}>
            Logout
          </Button>
          <Link to="/">
            <Button variant="outline" className="w-full">
              View Store
            </Button>
          </Link>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-card border-b">
          <div className="flex items-center justify-between px-6 py-4">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <div className="flex-1 lg:flex-none">
              <h2 className="text-lg font-medium text-foreground">Admin Workspace</h2>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
