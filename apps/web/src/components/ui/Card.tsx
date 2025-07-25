import React from 'react';
import clsx from 'clsx';
import styles from './Card.module.css';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined' | 'gradient';
  children: React.ReactNode;
  interactive?: boolean;
}

interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  noBorder?: boolean;
  tight?: boolean;
}

interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  tight?: boolean;
  loose?: boolean;
  noPadding?: boolean;
}

interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  noBorder?: boolean;
  center?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = 'default', children, interactive = false, ...props }, ref) => {
    const variants = {
      default: styles.default,
      elevated: styles.elevated,
      outlined: styles.outlined,
      gradient: styles.gradient
    };

    return (
      <div
        ref={ref}
        className={clsx(
          styles.card,
          variants[variant],
          {
            [styles.interactive]: interactive
          },
          className
        )}
        role={interactive ? 'button' : undefined}
        tabIndex={interactive ? 0 : undefined}
        {...props}
      >
        {children}
      </div>
    );
  }
);

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, children, noBorder = false, tight = false, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx(
        {
          [styles.cardHeader]: !noBorder && !tight,
          [styles.cardHeaderNoBorder]: noBorder,
          [styles.cardHeaderTight]: tight
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);

const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, children, tight = false, loose = false, noPadding = false, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx(
        {
          [styles.cardContent]: !tight && !loose && !noPadding,
          [styles.cardContentTight]: tight,
          [styles.cardContentLoose]: loose,
          [styles.cardContentNoPadding]: noPadding
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);

const CardFooter = React.forwardRef<HTMLDivElement, CardFooterProps>(
  ({ className, children, noBorder = false, center = false, ...props }, ref) => (
    <div
      ref={ref}
      className={clsx(
        {
          [styles.cardFooter]: !noBorder && !center,
          [styles.cardFooterNoBorder]: noBorder && !center,
          [styles.cardFooterCenter]: center
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);

Card.displayName = 'Card';
CardHeader.displayName = 'CardHeader';
CardContent.displayName = 'CardContent';
CardFooter.displayName = 'CardFooter';

export { Card, CardHeader, CardContent, CardFooter }; 