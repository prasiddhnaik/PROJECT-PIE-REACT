import React from 'react';
import clsx from 'clsx';
import styles from './Button.module.css';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'success';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    className,
    variant = 'primary',
    size = 'md',
    loading = false,
    leftIcon,
    rightIcon,
    children,
    disabled,
    ...props
  }, ref) => {
    const variants = {
      primary: styles.primary,
      secondary: styles.secondary,
      outline: styles.outline,
      ghost: styles.ghost,
      destructive: styles.destructive,
      success: styles.success
    };

    const sizes = {
      sm: styles.sm,
      md: styles.md,
      lg: styles.lg,
      xl: styles.xl
    };

    const iconSizes = {
      sm: styles.iconSm,
      md: styles.iconMd,
      lg: styles.iconLg,
      xl: styles.iconXl
    };

    const isDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        className={clsx(
          styles.button,
          variants[variant],
          sizes[size],
          {
            [styles.loading]: loading
          },
          className
        )}
        disabled={isDisabled}
        {...props}
      >
        {loading && (
          <div className={styles.spinner} />
        )}
        
        {!loading && leftIcon && (
          <span className={iconSizes[size]}>
            {leftIcon}
          </span>
        )}
        
        <span>{children}</span>
        
        {!loading && rightIcon && (
          <span className={iconSizes[size]}>
            {rightIcon}
          </span>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button }; 