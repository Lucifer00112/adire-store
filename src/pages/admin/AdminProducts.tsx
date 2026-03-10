import { useState } from 'react';
import { Plus, Search, Edit, Trash2, Eye } from 'lucide-react';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';

// Mock product data
const mockProducts = [
  { id: '1', name: 'Adire Buba for Men', price: 45.99, category: 'mens', stock: 24, status: 'active' },
  { id: '2', name: 'Adire Kaftan - Women', price: 55.99, category: 'womens', stock: 18, status: 'active' },
  { id: '3', name: 'Kids Adire Dress', price: 32.99, category: 'kids', stock: 32, status: 'active' },
  { id: '4', name: 'Traditional Agbada Set', price: 89.99, category: 'traditional', stock: 12, status: 'active' },
  { id: '5', name: 'Modern Adire Shirt', price: 38.99, category: 'modern', stock: 0, status: 'out-of-stock' },
  { id: '6', name: 'Adire Wrapper & Blouse', price: 65.99, category: 'womens', stock: 15, status: 'active' },
  { id: '7', name: 'Adire Head Tie (Gele)', price: 18.99, category: 'accessories', stock: 45, status: 'active' },
  { id: '8', name: 'Adire Fabric by Yard', price: 22.99, category: 'fabric', stock: 120, status: 'active' },
];

export default function AdminProducts() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    price: '',
    category: '',
    stock: '',
    description: '',
  });

  const filteredProducts = mockProducts.filter(product =>
    product.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission here
    console.log('Form submitted:', formData);
    setIsDialogOpen(false);
    setFormData({ name: '', price: '', category: '', stock: '', description: '' });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1>Products</h1>
          <p className="text-muted-foreground mt-1">
            Manage your Adire clothing inventory
          </p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Product
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <form onSubmit={handleSubmit}>
              <DialogHeader>
                <DialogTitle>Add New Product</DialogTitle>
                <DialogDescription>
                  Add a new product to your inventory
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Product Name</Label>
                  <Input
                    id="name"
                    placeholder="Enter product name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="price">Price ($)</Label>
                    <Input
                      id="price"
                      type="number"
                      step="0.01"
                      placeholder="0.00"
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="stock">Stock</Label>
                    <Input
                      id="stock"
                      type="number"
                      placeholder="0"
                      value={formData.stock}
                      onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <Select value={formData.category} onValueChange={(value) => setFormData({ ...formData, category: value })}>
                    <SelectTrigger id="category">
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="mens">Men's Wear</SelectItem>
                      <SelectItem value="womens">Women's Wear</SelectItem>
                      <SelectItem value="kids">Kids' Wear</SelectItem>
                      <SelectItem value="traditional">Traditional</SelectItem>
                      <SelectItem value="modern">Modern Styles</SelectItem>
                      <SelectItem value="accessories">Accessories</SelectItem>
                      <SelectItem value="fabric">Fabrics</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Input
                    id="description"
                    placeholder="Product description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit">Add Product</Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Products Table */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-medium">Product</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Category</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Price</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Stock</th>
                <th className="px-6 py-3 text-left text-sm font-medium">Status</th>
                <th className="px-6 py-3 text-right text-sm font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {filteredProducts.map((product) => (
                <tr key={product.id} className="hover:bg-muted/30">
                  <td className="px-6 py-4">
                    <p className="font-medium">{product.name}</p>
                    <p className="text-sm text-muted-foreground">ID: {product.id}</p>
                  </td>
                  <td className="px-6 py-4 capitalize">
                    <span className="text-sm">{product.category}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-medium">${product.price}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={product.stock === 0 ? 'text-destructive' : ''}>
                      {product.stock} units
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <Badge variant={product.status === 'active' ? 'default' : 'secondary'}>
                      {product.status}
                    </Badge>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end gap-2">
                      <Button variant="ghost" size="icon">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon">
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
