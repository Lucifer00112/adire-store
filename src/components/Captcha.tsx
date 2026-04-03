import { useState, useEffect, forwardRef, useImperativeHandle } from 'react';

export interface CaptchaHandle {
  validate: (input: string) => boolean;
  refresh: () => void;
}

export const Captcha = forwardRef<CaptchaHandle>((props, ref) => {
  const [captchaText, setCaptchaText] = useState('');

  const generateCaptcha = () => {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789';
    let text = '';
    for (let i = 0; i < 5; i++) {
        text += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setCaptchaText(text);
  };

  useEffect(() => {
    generateCaptcha();
  }, []);

  useImperativeHandle(ref, () => ({
    validate: (input: string) => input === captchaText,
    refresh: generateCaptcha
  }));

  return (
    <div className="flex flex-col items-center justify-center p-4 bg-[#FDF9F1] rounded-lg border border-[#4A0080]/20 mb-4 select-none">
      <p className="text-xs text-gray-500 mb-2 font-medium">SECURITY CHECK</p>
      <div 
        className="text-3xl font-mono tracking-[0.25em] font-bold text-[#4A0080]"
        style={{
          filter: 'drop-shadow(0px 2px 2px rgba(0,0,0,0.3)) blur(1.5px)',
          transform: 'skewX(-10deg) scaleY(1.1)',
          textShadow: '2px 2px 0px rgba(0, 0, 0, 0.1)'
        }}
      >
        {captchaText}
      </div>
      <button 
        type="button"
        onClick={generateCaptcha}
        className="text-xs text-[#4A0080]/70 hover:text-[#4A0080] mt-3 transition-colors cursor-pointer underline"
      >
        Click to generate a new word
      </button>
    </div>
  );
});
Captcha.displayName = 'Captcha';
