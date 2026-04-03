import { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Captcha, CaptchaHandle } from '../components/Captcha';
import { toast } from 'sonner';

export default function Auth() {
  const [isSignUpMode, setIsSignUpMode] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [captchaInput, setCaptchaInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  const captchaRef = useRef<CaptchaHandle>(null);
  const navigate = useNavigate();

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!captchaRef.current?.validate(captchaInput)) {
      toast.error('Incorrect security word. Please try again.');
      captchaRef.current?.refresh();
      setCaptchaInput('');
      return;
    }

    setIsLoading(true);
    try {
      const endpoint = isSignUpMode ? '/api/auth/signup' : '/api/auth/login';
      const body = isSignUpMode ? { email, password, name } : { email, password };

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      
      const data = await response.json();

      if (response.ok) {
        toast.success(isSignUpMode ? 'Account created successfully!' : 'Welcome back!');
        // Store simple token
        localStorage.setItem('customerToken', data.token || 'user-token');
        navigate('/');
      } else {
        toast.error(data.error || 'Authentication failed');
        captchaRef.current?.refresh();
        setCaptchaInput('');
      }
    } catch (error) {
      toast.error('Could not connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <Link to="/" className="flex justify-center mb-6 hover:opacity-80 transition-opacity">
          <span className="text-3xl font-serif italic font-bold text-primary">EURYTEXTILES</span>
        </Link>
        <h2 className="mt-6 text-center text-2xl font-extrabold text-foreground">
          {isSignUpMode ? 'Create your account' : 'Sign in to your account'}
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-card py-8 px-4 shadow-xl sm:rounded-2xl sm:px-10 border border-border">
          <div className="flex gap-4 mb-6">
            <button 
              onClick={() => setIsSignUpMode(false)} 
              type="button"
              className={`flex-1 pb-2 border-b-2 font-medium text-sm transition-colors ${!isSignUpMode ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
            >
              Sign In
            </button>
            <button 
              onClick={() => setIsSignUpMode(true)} 
              type="button"
              className={`flex-1 pb-2 border-b-2 font-medium text-sm transition-colors ${isSignUpMode ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
            >
              Create Account
            </button>
          </div>

          <form className="space-y-6" onSubmit={handleAuth}>
            {isSignUpMode && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                <Input
                  required
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email address</label>
              <Input
                required
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <Input
                required
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>

            <div className="pt-2">
              <Captcha ref={captchaRef} />
              <Input
                required
                type="text"
                placeholder="Type the security word above"
                value={captchaInput}
                onChange={(e) => setCaptchaInput(e.target.value)}
              />
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Processing...' : (isSignUpMode ? 'Sign Up' : 'Sign In')}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
