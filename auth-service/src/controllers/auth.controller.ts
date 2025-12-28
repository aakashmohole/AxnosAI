import { FastifyRequest } from 'fastify';
import { FastifyReply } from 'fastify';
import {
  Controller,
  Post,
  Body,
  Res,
  Req,
  UnauthorizedException,
  HttpStatus,
} from '@nestjs/common';
import { AuthService } from 'src/services/auth.service';
import { RegisterDto } from 'src/dto/register.dto';
import { LoginDto } from 'src/dto/login.dto';
import { JwtService } from '@nestjs/jwt';

@Controller('auth')
export class AuthController {
  constructor(
    private authService: AuthService,
    private jwtService: JwtService,
  ) {}

  @Post('register')
  async register(@Body() dto: RegisterDto, @Res() res: FastifyReply) {
    try {
      const result = await this.authService.register(
        dto.name,
        dto.email,
        dto.password,
      );
      return res.status(HttpStatus.OK).send({
        status: 'success',
        data: result,
      });
    } catch (error) {
      return res.status(HttpStatus.INTERNAL_SERVER_ERROR).send({
        status: 'error',
        message: 'Server error - ' + error,
      });
    }
  }

  @Post('login')
  async login(
    @Body() dto: LoginDto,
    @Res({ passthrough: true }) res: FastifyReply,
  ) {
    try {
      const result = await this.authService.login(dto.email, dto.password, res);
      return res.status(HttpStatus.OK).send({
        status: 'success',
        data: result,
      });
    } catch (error) {
      return res.status(HttpStatus.INTERNAL_SERVER_ERROR).send({
        status: 'error',
        message: 'Server error - ' + error,
      });
    }
  }

  @Post('refresh')
  async refresh(
    @Req() req: FastifyRequest,
    @Res({ passthrough: true }) res: FastifyReply,
  ) {
    const token = req.cookies['refreshToken'];
    if (!token) throw new UnauthorizedException('Missing refresh token');

    const decoded = await this.jwtService.verifyAsync(token, {
      secret: process.env.JWT_REFRESH_SECRET,
    });

    return this.authService.refresh(decoded.sub, token, res);
  }

  @Post('logout')
  async logout(
    @Req() req: FastifyRequest,
    @Res({ passthrough: true }) res: FastifyReply,
  ) {
    const token = req.cookies['refreshToken'];
    if (!token) throw new UnauthorizedException('Missing refresh token');

    const decoded = await this.jwtService.verifyAsync(token, {
      secret: process.env.JWT_REFRESH_SECRET,
    });

    return this.authService.logout(decoded.sub, res);
  }
}
