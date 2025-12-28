import { FastifyReply } from './../../node_modules/fastify/types/reply.d';
import {
  Injectable,
  UnauthorizedException,
  BadRequestException,
} from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { User } from 'src/schemas/user.schema';
import { Model } from 'mongoose';
import * as bcrypt from 'bcryptjs';
import { JwtService } from '@nestjs/jwt';

@Injectable()
export class AuthService {
  constructor(
    @InjectModel(User.name) private userModel: Model<User>,
    private jwtService: JwtService,
  ) {}

  async register(name: string, email: string, password: string) {
    try {
      const exists = await this.userModel.findOne({ email });
      if (exists) throw new BadRequestException('Email already in use');

      const hashedPassword = await bcrypt.hash(password, 10);

      const user = await this.userModel.create({
        name,
        email,
        password: hashedPassword,
      });

      const { password: hashPassword, ...result } = user.toObject();

      return result;
    } catch (error) {
      return error;
    }
  }

  async login(email: string, userPassword: string, res: FastifyReply) {
    const user = await this.userModel.findOne({ email });
    if (!user) throw new UnauthorizedException('Invalid credentials');

    const valid = await bcrypt.compare(userPassword, user.password);
    if (!valid) throw new UnauthorizedException('Invalid credentials');

    const accessToken = await this.jwtService.signAsync(
      { sub: user._id, email: user.email },
      { secret: process.env.JWT_SECRET, expiresIn: '2d' },
    );

    const newRefreshToken = await this.jwtService.signAsync(
      { sub: user._id },
      { secret: process.env.JWT_REFRESH_SECRET, expiresIn: '14d' },
    );

    user.refreshToken = await bcrypt.hash(newRefreshToken, 10);
    await user.save({ validateBeforeSave: false });

    res.setCookie('refreshToken', newRefreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'none',
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    const {password,refreshToken,...userRes} = user.toObject();


    return { accessToken,userRes };
  }

  async refresh(userId: string, refreshToken: string, res: FastifyReply) {
    const user = await this.userModel.findById(userId);
    if (!user || !user.refreshToken)
      throw new UnauthorizedException('Invalid refresh token');

    const valid = await bcrypt.compare(refreshToken, user.refreshToken);
    if (!valid) throw new UnauthorizedException('Invalid refresh token');

    const newAccessToken = await this.jwtService.signAsync(
      { sub: user._id, email: user.email },
      { secret: process.env.JWT_SECRET, expiresIn: '15m' },
    );

    const newRefreshToken = await this.jwtService.signAsync(
      { sub: user._id },
      { secret: process.env.JWT_REFRESH_SECRET, expiresIn: '7d' },
    );

    user.refreshToken = await bcrypt.hash(newRefreshToken, 10);
    await user.save();

    res.setCookie('refreshToken', newRefreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'none',
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    return { accessToken: newAccessToken };
  }

  async logout(userId: string, res: FastifyReply) {
    await this.userModel.findByIdAndUpdate(userId, { refreshToken: null });

    res.setCookie('refreshToken', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'none',
      maxAge: 0,
    });

    return { success: true, message: 'Logged out' };
  }
}
