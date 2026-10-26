"use client";
import { createContext, useContext } from 'react';
import type { dictionaries, Locale } from '@/lib/i18n';
export type Messages = typeof dictionaries.en;
const Context = createContext<{locale:Locale;messages:Messages}|null>(null);
export function LocaleProvider({locale,messages,children}:{locale:Locale;messages:Messages;children:React.ReactNode}) { return <Context.Provider value={{locale,messages}}>{children}</Context.Provider>; }
export function useLocale() { return useContext(Context); }
