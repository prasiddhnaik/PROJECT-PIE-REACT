import React from 'react';
import clsx from 'clsx';
import styles from './Badge.module.css';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'success' | 'error' | 'warning' | 'info' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  pulse?: boolean;
  icon?: React.ReactNode;
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'default', size = 'md', children, pulse = false, icon, ...props }, ref) => {
    const variants = {
      default: styles.default,
      success: styles.success,
      error: styles.error,
      warning: styles.warning,
      info: styles.info,
      outline: styles.outline
    };

    const sizes = {
      sm: styles.sm,
      md: styles.md,
      lg: styles.lg
    };

    const iconSizes = {
      sm: styles.iconSm,
      md: styles.iconMd,
      lg: styles.iconLg
    };

    return (
      <div
        ref={ref}
        className={clsx(
          styles.badge,
          variants[variant],
          sizes[size],
          {
            [styles.pulse]: pulse
          },
          className
        )}
        {...props}
      >
        {icon && (
          <span className={iconSizes[size]}>
            {icon}
          </span>
        )}
        {children}
      </div>
    );
  }
);

Badge.displayName = 'Badge';

export { Badge }; 