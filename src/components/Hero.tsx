import { Button } from './ui/button';
import { ImageWithFallback } from './figma/ImageWithFallback';

export function Hero() {
  return (
    <section className="bg-gradient-to-r from-primary/5 to-primary/10 py-16">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-2 gap-8 items-center">
          <div className="space-y-6">
            <h2 className="text-4xl md:text-5xl font-medium leading-tight">
              Authentic Adire Clothing & Fabrics
            </h2>
            <p className="text-lg text-muted-foreground">
              Discover the beauty of traditional Nigerian tie-dye. 
              From classic designs to modern interpretations, explore our collection of premium Adire clothing and fabrics.
            </p>
            <div className="flex gap-4">
              <Button size="lg">
                Shop Collection
              </Button>
              <Button variant="outline" size="lg">
                View Fabrics
              </Button>
            </div>
          </div>
          <div className="relative">
            <ImageWithFallback
              src="https://images.unsplash.com/photo-1594633313593-bab3825d0caf?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80"
              alt="Beautiful Adire clothing and fabrics"
              className="rounded-lg shadow-lg w-full h-80 object-cover"
            />
          </div>
        </div>
      </div>
    </section>
  );
}