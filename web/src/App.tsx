import { HStack, Box, Text, Link, IconButton, Button, useColorMode } from '@chakra-ui/react'
import { FaGithub } from 'react-icons/fa';
import { MdLightMode, MdDarkMode, MdChat } from 'react-icons/md';
import HeroIntroduction from './components/HeroIntroduction'
import PocketProfIcon from './assets/icon.png'

function App() {
  const { colorMode, toggleColorMode } = useColorMode()

  return (
    <>
      <IconButton
        onClick={toggleColorMode}
        isRound={true}
        icon={
          colorMode == 'dark'
            ? <MdLightMode />
            : <MdDarkMode />
        }
        aria-label={
          colorMode == 'dark'
            ? 'Light Mode'
            : 'Dark Mode'
        }
        position='fixed'
        bottom={8}
        right={8}
      />

      <HeroIntroduction title="Hey, I'm Pocket Prof.!" avatar={PocketProfIcon}>
        <Text fontSize='xl'>
          I am your one-stop solution to finding everything
        </Text>
        <Text fontSize='xl'>
          you need to know about NTU CS!
        </Text>

        <Box p={2} />

        <HStack>
          <Link href='https://t.me/pocketprof_bot' isExternal={true}>
            <Button leftIcon={<MdChat />}>Try me out!</Button>
          </Link>
          <Link href='https://github.com/Kaioru/pocketprof' isExternal={true}>
            <Button leftIcon={<FaGithub />}>Source Code</Button>
          </Link>
          {/* <Link href='mailto://keith@kaioru.co' isExternal={true}>
            <Button leftIcon={<MdOutlineEmail />}>Email</Button>
          </Link> */}
        </HStack>
      </HeroIntroduction>
    </>
  )
}

export default App;
