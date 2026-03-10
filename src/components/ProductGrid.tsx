import { useState, useMemo } from 'react';
import { ProductCard } from './ProductCard';
import { Product } from '../types';

const mockProducts: Product[] = [
  {
    id: '1',
    name: 'Adire Buba for Men',
    price: 45.99,
    image: 'https://images.unsplash.com/photo-1622445275463-afa2ab738c34?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'mens',
    description: 'Traditional Adire buba with intricate tie-dye patterns',
    rating: 4.8,
    inStock: true,
  },
  {
    id: '2',
    name: 'Adire Kaftan - Women',
    price: 55.99,
    image: 'https://images.unsplash.com/photo-1594633313593-bab3825d0caf?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'womens',
    description: 'Elegant flowing kaftan with traditional Adire designs',
    rating: 4.9,
    inStock: true,
  },
  {
    id: '3',
    name: 'Kids Adire Dress',
    price: 32.99,
    image: 'https://images.unsplash.com/photo-1622445275540-3346b193b29e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'kids',
    description: 'Beautiful Adire dress for children, comfortable and stylish',
    rating: 4.7,
    inStock: true,
  },
  {
    id: '4',
    name: 'Traditional Agbada Set',
    price: 89.99,
    image: 'https://images.unsplash.com/photo-1622445275463-afa2ab738c34?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'traditional',
    description: 'Complete traditional Agbada with Adire embellishments',
    rating: 4.9,
    inStock: true,
  },
  {
    id: '5',
    name: 'Modern Adire Shirt',
    price: 38.99,
    image: 'https://images.unsplash.com/photo-1622445275463-afa2ab738c34?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'modern',
    description: 'Contemporary fusion shirt with Adire patterns',
    rating: 4.6,
    inStock: true,
  },
  {
    id: '6',
    name: 'Adire Wrapper & Blouse',
    price: 65.99,
    image: 'https://images.unsplash.com/photo-1594633313593-bab3825d0caf?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'womens',
    description: 'Traditional wrapper and matching blouse set',
    rating: 4.8,
    inStock: true,
  },
  {
    id: '7',
    name: 'Adire Head Tie (Gele)',
    price: 18.99,
    image: 'https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'accessories',
    description: 'Premium Adire fabric head tie for special occasions',
    rating: 4.7,
    inStock: true,
  },
  {
    id: '8',
    name: 'Adire Fabric by Yard',
    price: 22.99,
    image: 'https://images.unsplash.com/photo-1603252109612-5372e7912b19?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'fabric',
    description: 'Authentic Adire fabric, sold per yard',
    rating: 4.8,
    inStock: true,
  },
  {
    id: '9',
    name: 'Men\'s Adire Senator Wear',
    price: 52.99,
    image: 'https://images.unsplash.com/photo-1622445275463-afa2ab738c34?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'mens',
    description: 'Stylish senator style with traditional Adire fabric',
    rating: 4.7,
    inStock: true,
  },
  {
    id: '10',
    name: 'Adire Maxi Dress',
    price: 58.99,
    image: 'https://images.unsplash.com/photo-1594633313593-bab3825d0caf?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'womens',
    description: 'Flowing maxi dress with vibrant Adire patterns',
    rating: 4.9,
    inStock: true,
  },
  {
    id: '11',
    name: 'Kids Adire Shorts Set',
    price: 28.99,
    image: 'https://images.unsplash.com/photo-1622445275540-3346b193b29e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'kids',
    description: 'Comfortable shorts and shirt set for children',
    rating: 4.6,
    inStock: true,
  },
  {
    id: '12',
    name: 'Adire Shoulder Bag',
    price: 35.99,
    image: 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'accessories',
    description: 'Handcrafted bag with Adire fabric accents',
    rating: 4.7,
    inStock: true,
  },
  {
    id: '13',
    name: 'Modern Adire Jumpsuit',
    price: 68.99,
    image: 'https://images.unsplash.com/photo-1594633313593-bab3825d0caf?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'modern',
    description: 'Contemporary jumpsuit with Adire design elements',
    rating: 4.8,
    inStock: true,
  },
  {
    id: '14',
    name: 'Traditional Iro & Buba',
    price: 72.99,
    image: 'https://images.unsplash.com/photo-1594633313593-bab3825d0caf?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'traditional',
    description: 'Classic Iro and Buba set in premium Adire fabric',
    rating: 4.9,
    inStock: true,
  },
  {
    id: '15',
    name: 'Adire Pocket Square Set',
    price: 15.99,
    image: 'https://images.unsplash.com/photo-1590874103328-eac38a683ce7?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'accessories',
    description: 'Set of 3 Adire pocket squares for formal occasions',
    rating: 4.5,
    inStock: true,
  },
  {
    id: '16',
    name: 'Premium Adire Fabric Roll',
    price: 95.99,
    image: 'https://images.unsplash.com/photo-1603252109612-5372e7912b19?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80',
    category: 'fabric',
    description: 'Full roll of authentic premium Adire fabric',
    rating: 4.9,
    inStock: true,
  },
];

interface ProductGridProps {
  onAddToCart: (product: Product) => void;
  selectedCategory: string;
  searchQuery: string;
}

export function ProductGrid({ onAddToCart, selectedCategory, searchQuery }: ProductGridProps) {
  const filteredProducts = useMemo(() => {
    let filtered = mockProducts;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(product => product.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(product =>
        product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return filtered;
  }, [selectedCategory, searchQuery]);

  return (
    <section className="py-12">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between mb-8">
          <h2>
            {selectedCategory === 'all' 
              ? 'All Products' 
              : `${selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)} Products`}
          </h2>
          <p className="text-muted-foreground">
            {filteredProducts.length} product{filteredProducts.length !== 1 ? 's' : ''}
          </p>
        </div>

        {filteredProducts.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No products found matching your criteria.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {filteredProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={onAddToCart}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}