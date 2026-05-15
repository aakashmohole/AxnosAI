import { NestFactory } from '@nestjs/core';
import {
  FastifyAdapter,
  NestFastifyApplication,
} from '@nestjs/platform-fastify';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import fastifyCookie from '@fastify/cookie';

async function bootstrap() {
  // 1. Pass options to the Fastify Adapter if needed, but Nest's enableCors usually hooks into it
  const app = await NestFactory.create<NestFastifyApplication>(
    AppModule,
    new FastifyAdapter(),
  );

  const frontendURL = process.env.FRONTEND_URL;

  // REMOVE app.use(cookieParser()) -> You are using Fastify, so use fastifyCookie instead!
  await app.register(fastifyCookie);

  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
  app.setGlobalPrefix('v1');

  // 2. Enable CORS BEFORE listening, and ensure preflight (OPTIONS) is explicitly handled
  app.enableCors({
    origin: frontendURL, // Can be a string directly
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    credentials: true,
    preflightContinue: false,
    optionsSuccessStatus: 204,
  });

  // '0.0.0.0' is perfect for allowing external network access
  await app.listen(process.env.PORT ?? 3001, '0.0.0.0');
}
bootstrap();
