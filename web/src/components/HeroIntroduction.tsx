import { ReactNode } from 'react';
import { Box, VStack, Heading, Image, Show, Hide, useColorModeValue, useToken } from '@chakra-ui/react'
import { Typewriter } from 'react-simple-typewriter'
import Hero from './Hero';

type Props = {
  title: string,
  avatar: string,
  children: ReactNode,
}

function HeroIntroduction({ title, avatar, children }: Props) {
  const bgGradientStart = useColorModeValue('#7b2243', 'green.600')
  const bgGradientEnd = useColorModeValue('blue.800', 'blue.400')
  const [bgGradientEndToken] = useToken(
    'colors',
    [bgGradientEnd]
  )

  return (
    <>
      <Hero>
        <Show below='lg'>
          <VStack>
            <Image boxSize='20vh' src={avatar} />
            <Box p={2} />
            <Heading
              as='h1'
              size='3xl'
              pb={1}
              bgGradient={`linear(to-r, ${bgGradientStart}, ${bgGradientEnd})`}
              bgClip='text'
            >
              <Typewriter
                words={[title]}
                cursor
                cursorStyle='_'
                cursorColor={bgGradientEndToken}
              />
            </Heading>
            {children}
          </VStack>
        </Show>

        <Hide below='lg'>
          <Box padding={20}>
            <Heading
              as='h1'
              size='3xl'
              minWidth={450}
              pb={2}
              bgGradient={`linear(to-r, ${bgGradientStart}, ${bgGradientEnd})`}
              bgClip='text'
            >
              <Typewriter
                words={[title]}
                cursor
                cursorStyle='_'
                cursorColor={bgGradientEndToken}
              />
            </Heading>
            {children}
          </Box>
          <Box padding={20}>
            <Image boxSize='40vh' src={avatar} />
          </Box>
        </Hide>
      </Hero>
    </>
  )
}

export default HeroIntroduction;
