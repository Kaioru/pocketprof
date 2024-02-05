import { ReactNode } from 'react';
import { Center } from '@chakra-ui/react'

type Props = {
  children: ReactNode
}

function Hero({ children }: Props) {
  return (
    <Center minWidth='max-content' minHeight='100vh'>
      {children}
    </Center>
  )
}

export default Hero;
